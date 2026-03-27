import os
import subprocess
import time
import datetime
from scripts.sentinel_reporter import report_error

# APIE Sentinel v11.2 - Intelligent Self-Healing (Backoff Strategy)
# NDA P-20260325-HEAL-V2

PROJECT_DIR = "/root/.openclaw/workspace/github_projects/prospect-intelligence"
STATE_FILE = os.path.join(PROJECT_DIR, "healer_state.json")
MAX_RETRY_ATTEMPTS = 5 # Límite de intentos antes de apagado de seguridad

def get_healer_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"attempts": 0, "last_failure": 0}

def save_healer_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def attempt_self_healing(error_context, error_msg):
    state = get_healer_state()
    now = time.time()
    
    # Reset de intentos si la última falla fue hace más de 1 hora (estabilidad recuperada)
    if now - state["last_failure"] > 3600:
        state["attempts"] = 0

    if state["attempts"] >= MAX_RETRY_ATTEMPTS:
        print("[HEALER] Límite de reintentos alcanzado. Apagado de seguridad para proteger IP.")
        return False

    state["attempts"] += 1
    state["last_failure"] = now
    save_healer_state(state)

    # CADENCIA DE ESPERA EXPONENCIAL (Estrategia de Backoff)
    # Intento 1: 5 min | 2: 15 min | 3: 30 min | 4: 1h | 5: 2h
    wait_times = [0, 300, 900, 1800, 3600, 7200]
    wait_seconds = wait_times[state["attempts"]]
    
    print(f"[HEALER] Intento {state['attempts']}/{MAX_RETRY_ATTEMPTS}. Esperando {wait_seconds/60:.0f} min...")
    
    if "Timeout" in error_msg or "403" in error_msg or "EPIPE" in error_msg:
        subprocess.run("ps aux | grep playwright | grep -v grep | awk '{print $2}' | xargs -r kill -9", shell=True)
        time.sleep(wait_seconds)
        recover_process()
        return True
    # ...

    # Caso 2: Error de Base de Datos (Locked)
    if "database is locked" in error_msg:
        print("[HEALER] DB bloqueada. Matando procesos zombis de python...")
        subprocess.run("ps aux | grep dgii_module_v10.py | grep -v grep | awk '{print $2}' | xargs -r kill -9", shell=True)
        time.sleep(5)
        recover_process()
        return True

    return False

def recover_process():
    """Lanza el orquestador en segundo plano."""
    try:
        # Usamos nohup para desacoplarlo del proceso sentinel
        subprocess.Popen(["nohup", ORCHESTRATOR_SCRIPT], 
                         stdout=open(os.devnull, 'w'), 
                         stderr=open(os.devnull, 'w'),
                         preexec_fn=os.setpgrp)
        print("[HEALER] Orquestador relanzado exitosamente.")
    except Exception as e:
        report_error("Self-Healer Recovery", f"Fallo crítico al intentar relanzar el proceso: {str(e)}")

if __name__ == "__main__":
    # Este módulo puede ser llamado por otros scripts ante excepciones
    pass
