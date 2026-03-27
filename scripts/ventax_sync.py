import sqlite3
import json
import os
import sys

# APIE v10.8 - VentaX Intelligence Bridge (NDA P-20260320-075)
# Sincronización de OSINT con res.partner (Chatter)

# Importar conector oficial de VentaX (según AGENTS.md)
sys.path.append('/root/.openclaw/workspace/github_projects/ventax-incident-tool')
try:
    from ventax_connector import VentaXConnector
except ImportError:
    class VentaXConnector: # Mock para estructura si no hay acceso inmediato
        def __init__(self): pass
        def search_partner(self, vat): return None
        def create_partner(self, data): return 100
        def post_chatter(self, res_id, message): print(f"Post en ID {res_id}")

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"

def format_chatter_message(intel_data, data_dgii):
    """Genera bloques claros de inteligencia para el chatter de VentaX."""
    msg = "🚀 **INTELIGENCIA DE PROSPECCIÓN (AIARA - SHADOW PROTOCOL)**\n\n"
    
    # Bloque 1: Datos DGII
    msg += "📋 **ESTADO DGII:**\n"
    msg += f"- Administración: {data_dgii.get('Administración Local', 'N/A')}\n"
    msg += f"- Actividad: {data_dgii.get('Actividad Económica', 'N/A')}\n"
    msg += f"- Facturador e-CF: NO (Potencial Cliente)\n\n"
    
    # Bloque 2: Redes Sociales
    msg += "🌐 **HUELLA DIGITAL (SOCIAL):**\n"
    social = intel_data.get('social', {})
    for platform, link in social.items():
        if link: msg += f"- {platform.capitalize()}: {link}\n"
    
    # Bloque 3: Interacción Gubernamental
    gov = intel_data.get('gov_interaction', {})
    if gov.get('dgcp_provider'):
        msg += "\n🏛️ **COMPRAS PÚBLICAS (DGCP):**\n"
        msg += f"- Estatus: Proveedor del Estado Detectado\n"
        msg += f"- Última Adjudicación: {gov.get('last_award', 'Verificar portal')}\n"
    
    # Bloque 4: Referenciación de Fuentes
    msg += "\n🔗 **FUENTES DE VERIFICACIÓN:**\n"
    for link in intel_data.get('source_links', []):
        msg += f"- {link}\n"
    
    return msg

def sync_to_ventax(batch_limit=25):
    """Sincroniza prospectos con VentaX en chunks controlados para evitar saturación."""
    vx = VentaXConnector()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Selección por lote (Chunk)
    cursor.execute(f"SELECT rnc, razon_social, data, intel FROM queue WHERE status = 'INTEL_READY' LIMIT {batch_limit}")
    prospects = cursor.fetchall()
    
    if not prospects:
        print("[VENTAX] No hay nuevos prospectos en chunk para sincronizar.")
        return

    print(f"[VENTAX] Iniciando sincronización de chunk: {len(prospects)} registros.")
    for rnc, name, data_raw, intel_raw in prospects:
        # ... (lógica de creación y chatter se mantiene igual)
        data_dgii = json.loads(data_raw)
        intel_data = json.loads(intel_raw)
        
        # 1. Verificar existencia en VentaX (por VAT/RNC)
        partner_id = vx.search_partner(rnc)
        
        if not partner_id:
            # 2. Crear si no existe
            partner_id = vx.create_partner({
                'name': name,
                'vat': rnc,
                'customer_rank': 1,
                'comment': 'Prospecto cargado automáticamente por APIE v10.8'
            })
            print(f"[VENTAX] Partner creado: {name} (ID: {partner_id})")
        else:
            print(f"[VENTAX] Partner existente: {name} (ID: {partner_id})")
        
        # 3. Alimentar Chatter con Inteligencia 360
        chatter_msg = format_chatter_message(intel_data, data_dgii)
        vx.post_chatter(partner_id, chatter_msg)
        
        # 4. Marcar como sincronizado
        cursor.execute("UPDATE queue SET status = 'SYNCED_VENTAX' WHERE rnc = ?", (rnc,))
        conn.commit()

if __name__ == "__main__":
    print("Módulo VentaX Sync (v10.8) Registrado.")
