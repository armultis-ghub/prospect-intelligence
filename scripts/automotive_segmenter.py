import sqlite3
import json
import os

# APIE v10.10 - Automotive Sector Segmenter
# NDA P-20260325-AUTO

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"

def segment_automotive():
    if not os.path.exists(DB_PATH): return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Asegurar que existe la columna de segmento si no existe
    try:
        cursor.execute("ALTER TABLE queue ADD COLUMN segment TEXT")
    except: pass
    
    # 2. Identificar registros de VENTA DE VEHÍCULOS AUTOMOTORES
    # Buscamos en el JSON de la columna 'data'
    cursor.execute("SELECT rnc, data FROM queue WHERE status = 'SUCCESS' AND segment IS NULL")
    rows = cursor.fetchall()
    
    count = 0
    for rnc, data_raw in rows:
        if not data_raw: continue
        data = json.loads(data_raw)
        activity = data.get('Actividad Económica', '').upper()
        
        if "VENTA DE VEHÍCULOS AUTOMOTORES" in activity or "VENTA DE VEHICULOS AUTOMOTORES" in activity:
            cursor.execute("UPDATE queue SET segment = 'AUTOMOTIVE' WHERE rnc = ?", (rnc,))
            count += 1
            
    conn.commit()
    conn.close()
    if count > 0:
        print(f"[SEGMENT] {count} nuevos prospectos asignados al segmento AUTOMOTIVE.")

if __name__ == "__main__":
    segment_automotive()
