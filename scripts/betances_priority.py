import sqlite3
import json
import os
import datetime

# APIE v10.16 - Betances Priority & November Intelligence
# NDA P-20260325-BETANCES-PRIORITY

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
BETANCES_RNC = "101006145"

def prioritize_betances_and_november():
    if not os.path.exists(DB_PATH): return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Prioridad Absoluta: LUIS E BETANCES R Y CO SAS
    cursor.execute("""
        UPDATE queue 
        SET segment = 'ULTRA_PRIORITY_BETANCES', 
            status = 'SUCCESS' 
        WHERE rnc = ?
    """, (BETANCES_RNC,))
    
    if cursor.rowcount > 0:
        print(f"[PRIORITY] RNC {BETANCES_RNC} (BETANCES) marcado como ULTRA_PRIORITY.")

    # 2. Marcar todos los de Noviembre para investigación inmediata
    cursor.execute("""
        UPDATE queue 
        SET segment = 'NOV_PRIORITY' 
        WHERE status = 'SUCCESS' 
        AND plazo LIKE '%noviembre%' 
        AND (segment IS NULL OR segment = '')
    """)
    nov_count = cursor.rowcount
    
    # 3. Asegurar que los de Noviembre en PENDING suban en la cola
    # (En este sistema la cola es por status PENDING/RETRY, pero podemos usar el segment para que scripts OSINT los tomen)
    cursor.execute("""
        UPDATE queue 
        SET segment = 'NOV_PENDING_PRIORITY' 
        WHERE status = 'PENDING' 
        AND plazo LIKE '%noviembre%'
    """)
    pending_nov = cursor.rowcount
            
    conn.commit()
    conn.close()
    
    print(f"[PRIORITY] {nov_count} prospectos de Noviembre listos para inteligencia.")
    print(f"[PRIORITY] {pending_nov} prospectos de Noviembre pendientes priorizados en cola.")

if __name__ == "__main__":
    prioritize_betances_and_november()
