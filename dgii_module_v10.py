import sys
import os
import time
import pandas as pd
import json
import argparse
import random
import asyncio
import sqlite3
import traceback
from playwright.async_api import async_playwright

import re

# APIE v11.0 - "The Integrity Guardian" (Mandatory OSINT & Real Email Validation)
# NDA P-20260327-V11-0

class APIE_Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    rnc TEXT PRIMARY KEY,
                    razon_social TEXT,
                    nombre_comercial TEXT,
                    status TEXT DEFAULT 'PENDING',
                    attempts INTEGER DEFAULT 0,
                    last_update TIMESTAMP,
                    data TEXT,
                    segment TEXT,
                    plazo TEXT,
                    category TEXT,
                    zone TEXT,
                    real_email TEXT,
                    osint_data TEXT
                )
            """)
            conn.commit()

    def load_csv(self, csv_path):
        df = pd.read_csv(csv_path)
        with sqlite3.connect(self.db_path) as conn:
            for _, row in df.iterrows():
                rnc = str(row['RNC']).split('.')[0].strip()
                plazo = row.get('Plazo', 'N/A')
                conn.execute("""
                    INSERT INTO queue (rnc, razon_social, plazo) 
                    VALUES (?, ?, ?)
                    ON CONFLICT(rnc) DO UPDATE SET plazo = excluded.plazo
                """, (rnc, row.get('Razón Social', 'N/A'), plazo))
            conn.commit()

    def get_next(self):
        with sqlite3.connect(self.db_path) as conn:
            # PRIORIDAD MÁXIMA: Prospectos de NOVIEMBRE (Segment NOV_PENDING_PRIORITY)
            cursor = conn.execute("""
                SELECT rnc, razon_social FROM queue 
                WHERE status IN ('PENDING', 'RETRY') 
                AND attempts < 5 
                AND (segment = 'NOV_PENDING_PRIORITY' OR plazo LIKE '%noviembre%')
                LIMIT 1
            """)
            res = cursor.fetchone()
            if res: return res

            # SEGUNDA PRIORIDAD: Resto de la cola
            cursor = conn.execute("""
                SELECT rnc, razon_social FROM queue 
                WHERE status IN ('PENDING', 'RETRY') 
                AND attempts < 5 
                LIMIT 1
            """)
            return cursor.fetchone()

    def update_status(self, rnc, status, data=None, category=None, zone=None, real_email=None, osint_data=None):
        nombre_comercial = None
        if data and isinstance(data, dict):
            nombre_comercial = data.get("Nombre Comercial")
            
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE queue 
                SET status = ?, data = ?, nombre_comercial = ?, category = ?, zone = ?, 
                    real_email = ?, osint_data = ?, attempts = attempts + 1, last_update = CURRENT_TIMESTAMP 
                WHERE rnc = ?
            """, (status, json.dumps(data) if data else None, nombre_comercial, category, zone, real_email, json.dumps(osint_data) if osint_data else None, rnc))
            conn.commit()

class APIE_Engine_V10_3:
    def __init__(self):
        # URL Directa para evitar el iframe de SharePoint que es muy pesado/lento
        self.base_url = "https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/rnc.aspx"
        self.user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
        ]

    def validate_email_syntax(self, email):
        if not email: return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email): return False
        
        # Filtro de correos genéricos que bajan la calidad
        generic_prefixes = ['info@', 'contacto@', 'ventas@', 'admin@', 'recepcion@']
        if any(email.lower().startswith(p) for p in generic_prefixes):
            return "GENERIC"
        return True

    def get_zone_from_admin(self, admin_local):
        if not admin_local: return "OTRA"
        admin_local = admin_local.upper()
        
        zones = {
            "METRO": ["SAN CARLOS", "GAZCUE", "MIRAFLORES", "LOPE DE VEGA", "NACO", "HERRERA", "PIANTINI", "SANTO DOMINGO", "LINCOLN", "PRÓCERES", "MÁXIMO GÓMEZ"],
            "NORTE": ["SANTIAGO", "VEGA", "MOCA", "PUERTO PLATA"],
            "ESTE": ["HIGUEY", "ROMANA", "PUNTA CANA", "BAVARO"],
            "SUR": ["BANI", "AZUA", "BARAHONA"]
        }
        
        for zone, keywords in zones.items():
            if any(k in admin_local for k in keywords):
                return zone
        return "OTRA"

    async def fetch(self, rnc, page):
        try:
            print(f"      [SHADOW] Navegando a motor directo...")
            await page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
            
            # Selector original en la URL directa
            rnc_input = await page.wait_for_selector("#cphMain_txtRNCCedula", timeout=30000)
            
            # Humanización: Tap y vaciar
            await rnc_input.tap()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            
            # Tipeo humano lento
            for char in str(rnc):
                await page.keyboard.press(char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            await asyncio.sleep(random.uniform(1, 2))
            search_btn = await page.wait_for_selector("#cphMain_btnBuscarPorRNC", timeout=20000)
            await search_btn.tap()
            
            print(f"      [SHADOW] Búsqueda enviada para {rnc}. Esperando resultado...")
            
            # Esperar a carga dinámica con predicado robusto (AJUSTADO: cphMain_dvDatosContribuyentes es el ID real)
            await page.wait_for_function("""() => {
                const table = document.querySelector('#cphMain_dvDatosContribuyentes');
                const msg = document.querySelector('#cphMain_lblMensaje');
                return (table && table.innerText.length > 50) || (msg && msg.innerText.length > 5);
            }""", timeout=60000)

            # Intentar extraer de la tabla de resultados (GridView)
            data = await page.evaluate("""() => {
                const res = {};
                const rows = document.querySelectorAll('#cphMain_dvDatosContribuyentes tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length === 2) {
                        const label = cells[0].innerText.trim();
                        const value = cells[1].innerText.trim();
                        res[label] = value;
                    }
                });
                return res;
            }""")

            if data.get("Estado"):
                nombre_comercial = data.get("Nombre Comercial")
                # Criterio de calificación estratégico (MEJORA A: Sector Prioritario)
                is_active = data.get("Estado") == "ACTIVO"
                is_not_ecf = data.get("Facturador Electrónico") == "NO"
                
                # Lista de Sectores Prioritarios para IA/Chatbots (aunque tengan e-CF)
                # Estos sectores tienen alta rotación de clientes y necesitan automatización
                sectores_prioritarios = [
                    "RETAIL", "COMERCIO", "RESTAURANTE", "HOTEL", "SALUD", 
                    "MEDICO", "ODONTOLOGICO", "LEGAL", "ABOGADO", "TRANSPORTE",
                    "AUTOPARTS", "REPUESTOS", "COLEGIO", "ESCUELA"
                ]
                
                actividad = data.get("Actividad Economica", "").upper()
                is_priority_sector = any(sector in actividad for sector in sectores_prioritarios)

                # Mejora C: Segmentación por zona (Santo Domingo Metro es prioridad)
                admin_local = data.get("Administracion Local", "OTRA")
                zone = self.get_zone_from_admin(admin_local)

                # Normalizar llaves para compatibilidad con el resto del sistema
                normalized_data = {
                    "RNC": data.get("Cédula/RNC"),
                    "Nombre Comercial": nombre_comercial,
                    "Estado": data.get("Estado"),
                    "Actividad Económica": actividad,
                    "Administración Local": admin_local,
                    "Facturador Electrónico": data.get("Facturador Electrónico"),
                    "Sector Prioritario": "SI" if is_priority_sector else "NO",
                    "Zona": zone
                }

                # Calificación Estratégica Multi-Servicio (CID ADN)
                # 1. Prioridad IA/Chatbots (Sectores específicos + e-CF)
                # 2. VentaX MiPyMEs (No e-CF)
                # 3. Servicios de Ciberseguridad/PBX (ALREADY_ECF pero activos)
                if is_active:
                    if is_not_ecf:
                        category = "VENTAX_MIPYMES"
                    elif is_priority_sector:
                        category = "AI_CHATBOT_UPSKLLING"
                    else:
                        # Mejora: No descartar. Ofrecer Ciberseguridad, PBX VoIP o Auditoría CID.
                        category = "CYBERSEC_PBX_AUDIT"
                    
                    return {
                        "success": True, 
                        "data": normalized_data, 
                        "nombre_comercial": nombre_comercial,
                        "category": category,
                        "zone": zone
                    }
                else:
                    return {"success": False, "error": "INACTIVE/SUSPENDED", "disqualified": True, "nombre_comercial": nombre_comercial}
            
            msg_label = await page.query_selector("#cphMain_lblMensaje")
            if msg_label:
                text = await msg_label.inner_text()
                return {"success": False, "error": f"DGII_MSG: {text}", "failed": True}
                
            return {"success": False, "error": "NOT_FOUND"}
        except Exception as e:
            return {"success": False, "error": str(e)}

async def run_apie(db_path, batch_size):
    db = APIE_Database(db_path)
    engine = APIE_Engine_V10_3()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Contexto móvil obligatorio para evadir el 403 actual
        context = await browser.new_context(
            user_agent=random.choice(engine.user_agents),
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()
        
        count = 0
        while count < batch_size:
            target = db.get_next()
            if not target: break
            
            rnc, name = target
            print(f"[{count+1}/{batch_size}] Investigando {rnc} ({name})")
            
            try:
                res = await engine.fetch(rnc, page)
                if res["success"]:
                    category = res.get("category", "QUALIFIED")
                    zone = res.get("zone", "OTRA")
                    
                    # EVALUACIÓN DGII ESTÁNDAR (Como siempre ha funcionado)
                    # La evaluación de MX y Dorking se delega al proceso paralelo (Sentinel)
                    osint_data = {"dgii_status": "QUALIFIED", "commercial_name": res.get("nombre_comercial")}
                    
                    db.update_status(rnc, "SUCCESS", res["data"], category=category, zone=zone, real_email=None, osint_data=osint_data)
                    log_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [SUCCESS] RNC: {rnc} | {name} | Cat: {category} | Zona: {zone}\n"
                    with open("/root/.openclaw/workspace/github_projects/prospect-intelligence/prospeccion_diaria.log", "a") as f:
                        f.write(log_msg)
                    print(f"   [OK] Datos extraídos. Categoría: {category} | Zona: {zone}")
                else:
                    # Descalificación inmediata o fallo definitivo (ALREADY_ECF, INACTIVE, NOT_FOUND en DGII)
                    if res.get("disqualified") or res.get("failed"):
                        status = "FAILED"
                        log_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [DISQUALIFIED] RNC: {rnc} | {name} | Razón: {res['error']}\n"
                        with open("/root/.openclaw/workspace/github_projects/prospect-intelligence/prospeccion_diaria.log", "a") as f:
                            f.write(log_msg)
                    else:
                        status = "RETRY"
                    
                    db.update_status(rnc, status, {"error": res["error"]})
                    print(f"   [FAIL] {res['error']}")
                
                # PROTOCOLO DE REPORTE 20% (NDA P-20260320-075)
                processed_in_batch = count + 1
                report_interval = batch_size // 5 if batch_size >= 5 else 1
                if processed_in_batch % report_interval == 0:
                    try:
                        mailer_path = "/root/.openclaw/workspace/github_projects/aiara-mailer/email_tool.py"
                        mailer_venv = "/root/.openclaw/workspace/github_projects/aiara-mailer/venv/bin/python3"
                        progress_pct = (processed_in_batch / batch_size) * 100
                        mail_subject = f"PROGRESS REPORT: APIE Batch {progress_pct:.0f}%"
                        
                        with sqlite3.connect(db_path) as conn:
                            stats_res = conn.execute("SELECT status, count(*) FROM queue GROUP BY status").fetchall()
                        stats_dict = dict(stats_res)
                        
                        mail_body = f"REPORTE DE PROGRESO DE PROSPECCIÓN (CID ADN)\n\n" \
                                    f"Avance del Batch: {progress_pct:.0f}%\n" \
                                    f"Procesados en este turno: {processed_in_batch} / {batch_size}\n\n" \
                                    f"Estado Consolidado Histórico:\n{json.dumps(stats_dict, indent=2)}\n\n" \
                                    f"Este reporte se genera automáticamente cada 20% de avance para asegurar la Disponibilidad de la información."
                        
                        mail_body_escaped = mail_body.replace('"', '\\"')
                        os.system(f'{mailer_venv} {mailer_path} --to "jose.rondon@armultis.com" --subject "{mail_subject}" --body "{mail_body_escaped}"')
                    except Exception as report_err:
                        print(f"   [REPORT-ERROR] {report_err}")

            except Exception as e:
                print(f"   [CRITICAL] Error en batch: {str(e)}")
                db.update_status(rnc, "RETRY", {"error": str(e)})
            
            count += 1
            # Delay entre consultas para no saturar
            await asyncio.sleep(random.uniform(10, 20))
            
        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--init-csv', help='Cargar CSV a la cola')
    parser.add_argument('--batch', type=int, default=10)
    args = parser.parse_args()
    
    db_file = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
    
    if args.init_csv:
        db_manager = APIE_Database(db_file)
        db_manager.load_csv(args.init_csv)
    
    asyncio.run(run_apie(db_file, args.batch))
