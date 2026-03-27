import csv
import json
import os

# Prospector Engine RD v2.2.1 (DGII Integration Fix)
# Corregido: Salto de cabecera y encoding
# NDA P-20260317-046

WORKSPACE_DIR = '/root/.openclaw/workspace'
DGII_CSV = os.path.join(WORKSPACE_DIR, 'GM_001_prospectos_dgii.csv')
PROSPECT_LOG = os.path.join(WORKSPACE_DIR, 'github_projects/prospector-engine/prospects_log.jsonl')

def process_dgii_list():
    if not os.path.exists(DGII_CSV):
        return

    count = 0
    with open(DGII_CSV, mode='r', encoding='latin-1') as f:
        # Saltar la primera linea de metadatos "Listado,,,"
        next(f)
        reader = csv.DictReader(f)
        for row in reader:
            rnc = row.get('RNC', '').strip()
            # Manejar caracteres especiales en el CSV latin-1
            name = row.get('Raz\xf3n Social', '').strip() or row.get('Razn Social', '').strip()
            
            if rnc and name:
                prospect = {
                    "source": "DGII_OFFICIAL_LIST",
                    "vat": rnc,
                    "name": name.upper(),
                    "nicho": "ECF",
                    "priority": "ALTO",
                    "status": "pending_enrichment"
                }
                
                with open(PROSPECT_LOG, 'a') as log_f:
                    log_f.write(json.dumps(prospect) + "\n")
                count += 1
                
    print(f"[EXITO] {count} prospectos de la DGII integrados para enriquecimiento.")

if __name__ == "__main__":
    process_dgii_list()
