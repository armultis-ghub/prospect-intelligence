import sqlite3
import os
import subprocess
import datetime

# Aiara APIE - Automated Local Monitor (Zero Tokens)
# NDA P-20260320-075

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
MAILER_PATH = "/root/.openclaw/workspace/github_projects/aiara-mailer/email_tool.py"
MAILER_VENV = "/root/.openclaw/workspace/github_projects/aiara-mailer/venv/bin/python"
RECIPIENT = "jose.rondon@armultis.com"

def get_stats():
    if not os.path.exists(DB_PATH):
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Conteo por plazos (Fase 4.1 Mayo vs Noviembre)
    cursor.execute("SELECT plazo, count(*) FROM queue WHERE status = 'SUCCESS' GROUP BY plazo")
    plazos = dict(cursor.fetchall())
    
    # Conteo general
    cursor.execute("SELECT status, count(*) FROM queue GROUP BY status")
    stats = dict(cursor.fetchall())
    
    # Obtener los últimos 5 calificados (Activos y NO Facturadores e-CF)
    cursor.execute("""
        SELECT rnc, razon_social, plazo
        FROM queue 
        WHERE status = 'SUCCESS' 
        ORDER BY last_update DESC 
        LIMIT 5
    """)
    recent = cursor.fetchall()
    conn.close()
    return stats, recent, plazos

def send_report():
    data = get_stats()
    if not data: return
    
    stats, recent, plazos = data
    success = stats.get('SUCCESS', 0)
    pending = stats.get('PENDING', 0)
    retry = stats.get('RETRY', 0)
    failed = stats.get('FAILED', 0)
    total = success + pending + retry + failed

    mayo = plazos.get('15 de mayo 2025', 0)
    noviembre = plazos.get('15 de noviembre 2025', 0)

    subject = f"APIE v10.7 - Reporte de Lote [MAYO:{mayo}/NOV:{noviembre}]"
    
    body = f"""REPORTE AUTOMATIZADO APIE (THE SHADOW PROTOCOL)
Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RESUMEN POR PLAZO (SUCCESS):
---------------------------
Mayo 2025: {mayo}
Noviembre 2025: {noviembre}

RESUMEN GENERAL DE COLA:
---------------------------
Exitosos (SUCCESS): {success}
Pendientes (PENDING): {pending}
Reintentos (RETRY): {retry}
Fallidos (FAILED): {failed}
Total: {total}

ULTIMOS PROSPECTOS CALIFICADOS:
---------------------------
"""
    for rnc, name, plazo in recent:
        body += f"- {rnc} | {name} [{plazo}]\n"

    body += "\nEste es un reporte local generado por el orquestador maestro (0 Tokens)."

    try:
        subprocess.run([
            MAILER_VENV, 
            MAILER_PATH, 
            "--to", RECIPIENT, 
            "--subject", subject, 
            "--body", body
        ], check=True)
    except Exception as e:
        print(f"Error enviando correo: {e}")

if __name__ == "__main__":
    send_report()
