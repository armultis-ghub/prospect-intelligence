#!/bin/bash

# Aiara Zero-Token Orchestrator v1.0
# NDA P-20260402-ZTO

WORKSPACE="/root/.openclaw/workspace/github_projects/prospect-intelligence"
VENV="$WORKSPACE/venv/bin/python3"
LOG_FILE="$WORKSPACE/osint_worker.log"

echo "[$(date)] Iniciando orquestador Zero-Tokens..." >> $LOG_FILE

while true; do
    # 1. Ejecutar DGII Module (Extracción de RNC y categorización inicial)
    echo "[$(date)] Turno: Extracción DGII..." >> $LOG_FILE
    $VENV $WORKSPACE/dgii_module_v10.py --batch 5 >> $LOG_FILE 2>&1
    
    # 2. Ejecutar Correlacionador Legal (Reconsideraciones - 0 Tokens)
    echo "[$(date)] Turno: Correlación Legal (Reconsideraciones)..." >> $LOG_FILE
    $VENV $WORKSPACE/legal_correlator.py >> $LOG_FILE 2>&1

    # 3. Ejecutar OSINT Harvester (Google Dorking sin tokens)
    echo "[$(date)] Turno: OSINT Harvesting (Dorks)..." >> $LOG_FILE
    $VENV $WORKSPACE/osint_harvester.py --batch 3 >> $LOG_FILE 2>&1
    
    # 4. Pausa estratégica
    echo "[$(date)] Ciclo completado. Esperando 5 minutos..." >> $LOG_FILE
    sleep 300
done
