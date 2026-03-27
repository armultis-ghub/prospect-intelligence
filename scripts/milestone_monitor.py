import sqlite3
import os
import subprocess
import json

# APIE v10.9 - Progress Milestone Monitor (20% Thresholds)
# NDA P-20260325-MILESTONE

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
STATE_FILE = "/root/.openclaw/workspace/github_projects/prospect-intelligence/milestone_state.json"
MAILER_PATH = "/root/.openclaw/workspace/github_projects/aiara-mailer/email_tool.py"
MAILER_VENV = "/root/.openclaw/workspace/github_projects/aiara-mailer/venv/bin/python"
RECIPIENT = "jose.rondon@armultis.com"

def check_milestones():
    if not os.path.exists(DB_PATH): return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Obtener Total de Oportunidades Reales (SUCCESS + INTEL_READY + SYNCED)
    cursor.execute("SELECT count(*) FROM queue WHERE status IN ('SUCCESS', 'INTEL_READY', 'SYNCED_VENTAX', 'INTEL_WAIT') OR (status = 'FAILED' AND data NOT LIKE '%DISQUALIFIED%')")
    # Nota: Usamos una consulta más simple basada en los que NO fueron descalificados y ya se procesaron
    cursor.execute("SELECT count(*) FROM queue WHERE status NOT IN ('PENDING', 'RETRY') AND data NOT LIKE '%DISQUALIFIED%'")
    current_ready = cursor.fetchone()[0]
    
    # Obtener el total histórico de la base cargada
    cursor.execute("SELECT count(*) FROM queue")
    total_db = cursor.fetchone()[0]
    
    # Estimación de Oportunidades Reales Totales (basado en tasa de calificación actual)
    # Si no tenemos suficientes datos, usamos el total de la DB para el cálculo del 20%
    milestone_step = total_db // 5 # 20% del total cargado
    
    if current_ready == 0: return

    # 2. Cargar estado previo
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    else:
        state = {"last_milestone_percent": 0}

    current_percent = (current_ready * 100) // total_db
    
    # 3. Verificar si cruzamos un umbral de 20% (20, 40, 60, 80, 100)
    next_threshold = ((state["last_milestone_percent"] // 20) + 1) * 20
    
    if current_percent >= next_threshold:
        send_milestone_report(current_percent, current_ready, total_db)
        state["last_milestone_percent"] = (current_percent // 20) * 20
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

def send_milestone_report(percent, count, total):
    subject = f"APIE Milestone: {percent}% de la base procesada ({count} registros)"
    body = f"""REPORTE DE PROGRESO ESTRATÉGICO - APIE v10.9
Hito alcanzado: {percent}% de procesamiento alcanzado.

DETALLES:
-----------------------------------------------------------
- Registros procesados (no pendientes): {count}
- Total en base de datos: {total}
- Estado de Oportunidades: Revisar VentaX / Reportes de Lote.

El sistema continuará con el dorking de inteligencia y sincronización para este bloque.
Este reporte es automático (0 Tokens).
"""
    try:
        subprocess.run([MAILER_VENV, MAILER_PATH, "--to", RECIPIENT, "--subject", subject, "--body", body], check=True)
    except: pass

if __name__ == "__main__":
    check_milestones()
