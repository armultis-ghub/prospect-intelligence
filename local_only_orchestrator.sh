#!/bin/bash

# Aiara Local-Only Intelligence Orchestrator v2.0
# NDA P-20260402-LOI
# Objetivo: Investigar EXCLUSIVAMENTE sobre la base local. Cero prospección DGII.

WORKSPACE="/root/.openclaw/workspace/github_projects/prospect-intelligence"
VENV="$WORKSPACE/venv/bin/python3"
LOG_FILE="$WORKSPACE/local_intelligence.log"

echo "[$(date)] >>> INICIANDO ORQUESTADOR DE INTELIGENCIA LOCAL (NO DGII) <<<" >> $LOG_FILE

while true; do
    # 1. Ejecutar Correlacionador Legal (Reconsideraciones sobre base local - 0 Tokens)
    # Solo procesa lo que ya está en SUCCESS en la DB local.
    echo "[$(date)] Turno: Correlación Legal (Reconsideraciones)..." >> $LOG_FILE
    $VENV $WORKSPACE/legal_correlator.py >> $LOG_FILE 2>&1

    # 2. Ejecutar OSINT Harvester (Dorks sobre base local - 0 Tokens)
    # PRIORIDAD: Aquellos que NO son facturadores electrónicos (category = 'VENTAX_MIPYMES')
    echo "[$(date)] Turno: OSINT Harvesting (Dorks)..." >> $LOG_FILE
    # El script osint_harvester.py ya filtra por SUCCESS y sin email.
    $VENV $WORKSPACE/osint_harvester.py --batch 5 >> $LOG_FILE 2>&1
    
    # 3. Pausa estratégica humanizada
    echo "[$(date)] Ciclo local completado. Esperando 5 minutos..." >> $LOG_FILE
    sleep 300
done
