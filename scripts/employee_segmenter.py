import sqlite3
import json
import os

# APIE v10.11 - Employee (Salaried) Segmenter
# NDA P-20260325-EMPLOYEE

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"

def segment_employees():
    if not os.path.exists(DB_PATH): return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Asegurar que existe la columna de segmento si no existe
    try:
        cursor.execute("ALTER TABLE queue ADD COLUMN segment TEXT")
    except: pass
    
    # 2. Identificar EMPLEADOS (ASALARIADOS)
    # Buscamos en el JSON de la columna 'data' (Actividad Económica)
    cursor.execute("SELECT rnc, data FROM queue WHERE status = 'SUCCESS' AND (segment IS NULL OR segment != 'EMPLOYEE')")
    rows = cursor.fetchall()
    
    count = 0
    for rnc, data_raw in rows:
        if not data_raw: continue
        try:
            data = json.loads(data_raw)
            # El campo puede venir del motor de la DGII como "Actividad Económica"
            activity = str(data.get('Actividad Económica', '')).upper()
            
            # Criterios de segmentación para empleados/asalariados
            if any(term in activity for term in ["EMPLEADOS", "ASALARIADOS", "EMPLEADO", "ASALARIADO"]):
                cursor.execute("UPDATE queue SET status = 'SUCCESS', segment = 'EMPLOYEE' WHERE rnc = ?", (rnc,))
                count += 1
            # Segmentar personas físicas de la cola de pendientes que probablemente son empleados
            # (RNC de 11 dígitos que no tengan nombres comerciales de empresas)
        except Exception as e:
            continue
    
    # 3. Pre-segmentar personas físicas en PENDING que podrían ser empleados/asalariados
    # Basado en longitud de RNC (11 dígitos = Cédula)
    cursor.execute("""
        UPDATE queue 
        SET segment = 'POTENTIAL_EMPLOYEE' 
        WHERE status = 'PENDING' 
        AND length(rnc) = 11 
        AND segment IS NULL
    """)
    pe_count = cursor.rowcount
            
    conn.commit()
    conn.close()
    if count > 0:
        print(f"[SEGMENT] {count} prospectos asignados al segmento EMPLOYEE (ASALARIADOS).")
    if pe_count > 0:
        print(f"[SEGMENT] {pe_count} prospectos marcados como POTENTIAL_EMPLOYEE.")

if __name__ == "__main__":
    segment_employees()
