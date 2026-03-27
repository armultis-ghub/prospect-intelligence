import sqlite3
import json
import time
import subprocess
import os

# Aiara APIE - Villa Mella High Impact Campaign (Zero Tokens Orchestration)
# NDA P-20260320-075

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
MAILER_PATH = "/root/.openclaw/workspace/github_projects/aiara-mailer/email_tool.py"
MAILER_VENV = "/root/.openclaw/workspace/github_projects/aiara-mailer/venv/bin/python"
WHATSAPP_CONTACT = "+18292542767"

def get_vm_prospects():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rnc, razon_social, data FROM queue WHERE status = 'SUCCESS'")
    results = cursor.fetchall()
    conn.close()
    
    vm_prospects = []
    for rnc, name, data_raw in results:
        if not data_raw: continue
        data = json.loads(data_raw)
        # Solo ADM LOCAL VILLA MELLA y que NO sean facturadores electrónicos ya
        if 'Administración Local' in data and 'VILLA MELLA' in data['Administración Local'].upper():
            if data.get('Facturador Electrónico') == 'NO':
                vm_prospects.append({
                    "rnc": rnc,
                    "name": name,
                    "activity": data.get("Actividad Económica", "Comercio General")
                })
    return vm_prospects

def generate_body(name, activity, intel):
    # Lógica de Anclaje de Confianza (Referenciación de fuentes)
    anchor_text = ""
    if intel.get('gov_interaction', {}).get('dgcp_provider'):
        award = intel['gov_interaction'].get('last_award', 'procesos de compra estatal')
        anchor_text = f"Observamos su participación en {award}; como proveedores del Estado, la precisión en sus e-CF es crítica.\n"
    
    social_text = ""
    if intel.get('social', {}).get('instagram'):
        social_text = f"Vimos su reciente actividad en Instagram; nos impresiona su presencia de marca en el sector de {activity}.\n"

    return f"""Estimados directivos de {name},

Le saludamos desde AR Multiservices InT (ARMULTIS).

{anchor_text}{social_text}
Hemos identificado que su empresa se encuentra bajo la jurisdicción de la ADM LOCAL VILLA MELLA y, según registros de transparencia y cumplimiento, aún no ha completado la transición hacia la Facturación Electrónica (e-CF) obligatoria..."""

def run_campaign():
    # Esta función se ejecutará cuando el listado total esté procesado
    # Por ahora, preparamos la lógica
    prospects = get_vm_prospects()
    print(f"Iniciando campaña personalizada para {len(prospects)} prospectos de Villa Mella...")
    
    for p in prospects:
        subject = f"Propuesta de Facturación Electrónica para {p['name']} (Prioridad Villa Mella)"
        body = generate_body(p['name'], p['activity'])
        
        # Nota: En producción buscaremos el correo en la DB (si se capturó) 
        # o usaremos el sistema de prospección para hallarlo.
        # Por ahora, registramos la intención de envío.
        print(f"Generando correo para: {p['name']} - {p['activity']}")
        
        # Simulación de envío (requiere email de destino real)
        # subprocess.run([MAILER_VENV, MAILER_PATH, "--to", "target@example.com", "--subject", subject, "--body", body])

if __name__ == "__main__":
    # Esta es una pre-configuración. No se dispara masivamente hasta el final del escaneo.
    print("Módulo de Campaña Villa Mella Registrado.")
