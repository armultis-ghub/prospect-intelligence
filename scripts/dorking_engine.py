import sqlite3
import json
import os
import subprocess

# APIE v10.20 - Dorking Intelligence Engine (Nombre Comercial)
# NDA P-20260325-DORKING

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"

def run_dorking_on_commercial_names():
    if not os.path.exists(DB_PATH): return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Seleccionar prospectos SUCCESS con Nombre Comercial que no tengan dorking en su segment/data
    # MODIFICACIÓN: Si no hay Nombre Comercial, usar Razón Social
    cursor.execute("SELECT rnc, razon_social, data FROM queue WHERE status = 'SUCCESS' AND segment != 'DORKED'")
    rows = cursor.fetchall()
    
    for rnc, name, data_raw in rows:
        if not data_raw: continue
        data = json.loads(data_raw)
        nombre_comercial = data.get("Nombre Comercial")
        
        # Prioridad: 1. Nombre Comercial, 2. Razón Social
        target_name = nombre_comercial if nombre_comercial and nombre_comercial != "N/A" else name
        
        if target_name:
            print(f"[DORKING] Investigando: {target_name} (RNC: {rnc})")
            # Aquí se ejecutaría el comando de búsqueda OSINT (simulado para este flujo)
            # En producción, esto llamaría a un sub-proceso que guarde en el chatter de VentaX
            
            # Marcar como procesado para evitar duplicidad
            cursor.execute("UPDATE queue SET segment = 'DORKED' WHERE rnc = ?", (rnc,))
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_dorking_on_commercial_names()
