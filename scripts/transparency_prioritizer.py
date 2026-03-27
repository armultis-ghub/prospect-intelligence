import sys
import os
import json
import datetime

# Módulo de Priorización: Transparencia y Proveedores del Estado (NDA P-20260317-051)
# Este script reordena la cola de prospección para atacar primero el segmento B2G/B2B de alto perfil.

WORKSPACE_DIR = '/root/.openclaw/workspace'
PROSPECT_LOG = os.path.join(WORKSPACE_DIR, 'github_projects/prospector-engine/prospects_log.jsonl')
PRIORITY_LOG = os.path.join(WORKSPACE_DIR, 'github_projects/prospector-engine/transparency_priority_queue.jsonl')

KEYWORDS_TRANSPARENCIA = ["CONSTRUCTORA", "INGENIERIA", "SERVICIOS MEDICOS", "TECNOLOGIA", "SUMINISTROS"]

def prioritize_transparency_prospects():
    """Identifica prospectos con alta probabilidad de ser proveedores del estado."""
    if not os.path.exists(PROSPECT_LOG):
        print("[ERROR] No hay prospectos registrados para priorizar.")
        return

    count = 0
    with open(PROSPECT_LOG, 'r') as f, open(PRIORITY_LOG, 'w') as out:
        for line in f:
            try:
                p = json.loads(line)
                # Priorizar por palabras clave en el nombre (Sectores que venden al estado)
                is_priority = any(kw in p['name'] for kw in KEYWORDS_TRANSPARENCIA)
                
                if is_priority:
                    p['priority_tag'] = "GOV_SUPPLIER_CANDIDATE"
                    p['priority_level'] = 1 # Máxima prioridad
                    out.write(json.dumps(p) + "\n")
                    count += 1
            except: continue
                
    print(f"[EXITO] {count} empresas identificadas como candidatas prioritarias (Transparencia).")

if __name__ == "__main__":
    print("--- Priorizador de Transparencia v1.0.0 ---")
    prioritize_transparency_prospects()
