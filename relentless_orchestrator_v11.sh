#!/bin/bash
# RELENTLESS ORCHESTRATOR v11.5 - "The Relentless Guardian"
# NDA P-20260327-V11-5
# Este orquestador asegura el procesamiento TOTAL de la cola con prioridad NOVIEMBRE.

PROJECT_DIR="/root/.openclaw/workspace/github_projects/prospect-intelligence"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
LOG_FILE="$PROJECT_DIR/apie_background_v10.log"
DB_FILE="$PROJECT_DIR/apie_v10.db"

echo "[ORCHESTRATOR] Iniciando Ciclo Relentless (ADN CID)..."

while true; do
    # 1. Verificar prospectos pendientes
    PENDING_TOTAL=$(sqlite3 "$DB_FILE" "SELECT count(*) FROM queue WHERE status IN ('PENDING', 'RETRY');")
    PENDING_NOV=$(sqlite3 "$DB_FILE" "SELECT count(*) FROM queue WHERE status IN ('PENDING', 'RETRY') AND (segment = 'NOV_PENDING_PRIORITY' OR plazo LIKE '%noviembre%');")

    if [ "$PENDING_TOTAL" -eq 0 ]; then
        echo "[ORCHESTRATOR] Cola totalmente procesada. Finalizando ciclo."
        break
    fi

    echo "[ORCHESTRATOR] $(date) - Pendientes: $PENDING_TOTAL (Noviembre: $PENDING_NOV). Ejecutando batch de 500..."
    
    # 2. Ejecutar lote de procesamiento
    $VENV_PYTHON "$PROJECT_DIR/dgii_module_v10.py" --batch 500 >> "$LOG_FILE" 2>&1
    
    # 3. Pausa de seguridad para Disponibilidad del servidor (Cool-down)
    echo "[ORCHESTRATOR] Batch completado. Enfriamiento de 60s..."
    sleep 60
done

echo "[ORCHESTRATOR] $(date) - Operación finalizada con éxito."
