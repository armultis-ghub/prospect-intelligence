import sys
import os
import subprocess
import datetime
import traceback

# APIE Sentinel v11.0 - Automated Incident Reporter (Zero Tokens)
# NDA P-20260320-075

MAILER_PATH = "/root/.openclaw/workspace/github_projects/aiara-mailer/email_tool.py"
MAILER_VENV = "/root/.openclaw/workspace/github_projects/aiara-mailer/venv/bin/python"
ADMIN_EMAIL = "jose.rondon@armultis.com"

from scripts.self_healer import attempt_self_healing

def report_error(context, error_msg, stack_trace=None):
    # ... (lógica de envío de correo actual)
    
    # NUEVA CAPACIDAD v11.1: Auto-Subsanación
    healed = attempt_self_healing(context, error_msg)
    if healed:
        print(f"[SENTINEL] Subsanación automática aplicada con éxito para {context}")

def global_exception_handler(exctype, value, tb):
    """Captura excepciones no manejadas y las reporta."""
    error_msg = str(value)
    stack_trace = "".join(traceback.format_exception(exctype, value, tb))
    report_error("Global Handler (Uncaught Exception)", error_msg, stack_trace)
    sys.__excepthook__(exctype, value, tb)

if __name__ == "__main__":
    # Prueba del sistema de alerta
    report_error("Prueba Sentinel", "Simulación de error en motor de inteligencia")
