import sqlite3
import json
import os
import subprocess
import time

# APIE v10.15 - November Priority Investigator
# NDA P-20260325-NOV-PRIORITY

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
PROJECT_DIR = "/root/.openclaw/workspace/github_projects/prospect-intelligence"

def prioritize_november():
    if not os.path.exists(DB_PATH): return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Identificar prospectos de noviembre que ya son SUCCESS pero no han sido investigados OSINT
    # Según MEMORY.md, la Fase 4.1 y 5 se ejecutan post-SUCCESS.
    # Aquí vamos a marcarlos para que los scripts de inteligencia los procesen primero.
    
    cursor.execute("""
        SELECT rnc, razon_social FROM queue 
        WHERE status = 'SUCCESS' 
        AND plazo LIKE '%noviembre%'
    """)
    nov_targets = cursor.fetchall()
    
    if nov_targets:
        print(f"[PRIORITY] Iniciando inteligencia profunda para {len(nov_targets)} prospectos de Noviembre...")
        # Nota: Aquí se integrarían llamadas a los scripts de Google Dorking y OSINT
        # Por ahora, aseguramos que el segmentador y otros procesos los tengan en cuenta.
        for rnc, name in nov_targets:
            # Marcar segmento si no tiene uno más específico
            cursor.execute("UPDATE queue SET segment = 'NOV_PRIORITY' WHERE rnc = ? AND segment IS NULL", (rnc,))
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    prioritize_november()
