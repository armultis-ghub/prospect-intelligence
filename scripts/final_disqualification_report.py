import sqlite3
import os
import json
import datetime
import subprocess

# Aiara APIE - Final Disqualification & Intelligence Report (Zero Tokens)
# NDA P-20260325-REPORT

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
MAILER_PATH = "/root/.openclaw/workspace/github_projects/aiara-mailer/email_tool.py"
MAILER_VENV = "/root/.openclaw/workspace/github_projects/aiara-mailer/venv/bin/python"
RECIPIENT = "jose.rondon@armultis.com"

def generate_final_report():
    if not os.path.exists(DB_PATH):
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Estadísticas de Descalificación
    cursor.execute("SELECT count(*) FROM queue WHERE status = 'FAILED' AND data LIKE '%ALREADY_ECF%'")
    already_ecf = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM queue WHERE status = 'FAILED' AND data LIKE '%INACTIVE%'")
    inactive = cursor.fetchone()[0]
    
    # 2. Estadísticas de Calificación (Oportunidades Reales)
    cursor.execute("SELECT count(*) FROM queue WHERE status IN ('SUCCESS', 'INTEL_READY')")
    qualified = cursor.fetchone()[0]
    
    # 3. Prospectos de Villa Mella (Foco)
    cursor.execute("SELECT count(*) FROM queue WHERE status IN ('SUCCESS', 'INTEL_READY') AND data LIKE '%VILLA MELLA%'")
    villa_mella_ops = cursor.fetchone()[0]
    
    total_processed = already_ecf + inactive + qualified
    
    subject = f"APIE v10.6 - Informe de Calificación Final [Muestra: {total_processed}]"
    
    body = f"""INFORME ESTRATÉGICO DE CALIFICACIÓN DE PROSPECTOS
Protocolo: The Shadow Protocol (v10.6)
Fecha de Corte: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1. RESUMEN DE DESCALIFICACIÓN (DESCARTE)
-----------------------------------------------------------
- Ya son Facturadores e-CF: {already_ecf}
- Empresas Suspendidas/Inactivas: {inactive}
- Total Descartados: {already_ecf + inactive}

2. RESUMEN DE OPORTUNIDADES (CALIFICADOS)
-----------------------------------------------------------
- Prospectos Activos y NO e-CF: {qualified}
- Foco Prioritario (Villa Mella): {villa_mella_ops}

3. CONCLUSIÓN TÉCNICA
-----------------------------------------------------------
El {((already_ecf + inactive) / total_processed * 100) if total_processed > 0 else 0:.1f}% de la base de datos fue filtrada automáticamente por no cumplir con el perfil comercial. 
Se ha evitado el uso innecesario de recursos en {already_ecf + inactive} empresas.

Este reporte fue generado de forma autónoma (0 Tokens).
"""
    
    try:
        subprocess.run([MAILER_VENV, MAILER_PATH, "--to", RECIPIENT, "--subject", subject, "--body", body], check=True)
        print("Informe final enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar informe: {e}")
    
    conn.close()

if __name__ == "__main__":
    generate_final_report()
