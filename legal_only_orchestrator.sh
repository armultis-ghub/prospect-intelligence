#!/bin/bash

# Aiara Legal Sentinel Orchestrator - Priority Reconsideration
# NDA P-20260402-LSO
# Objetivo: Correlación EXCLUSIVA de Reconsideraciones sobre base local.

WORKSPACE="/root/.openclaw/workspace/github_projects/prospect-intelligence"
VENV="$WORKSPACE/venv/bin/python3"
LOG_FILE="$WORKSPACE/legal_priority_only.log"

echo "[$(date)] >>> INICIANDO ORQUESTADOR DE CORRELACIÓN LEGAL PRIORITARIA <<<" >> $LOG_FILE
echo "[$(date)] Operación: Solo Recursos de Reconsideración DGII." >> $LOG_FILE

while true; do
    # Ejecutar Correlacionador Legal (Reconsideraciones - 0 Tokens)
    # Este script ya analiza todos los prospectos SUCCESS en la DB.
    echo "[$(date)] Iniciando escaneo de Reconsideraciones..." >> $LOG_FILE
    $VENV $WORKSPACE/legal_correlator.py >> $LOG_FILE 2>&1
    
    # Reporte de hallazgos actuales para el log
    MATCHES=$(sqlite3 $WORKSPACE/apie_v10.db "SELECT COUNT(*) FROM queue WHERE osint_data LIKE '%legal_issues%' AND osint_data LIKE '%\"has_reconsiderations\": true%';")
    echo "[$(date)] Hallazgos críticos acumulados: $MATCHES" >> $LOG_FILE

    # Pausa entre escaneos para actualización de fuentes (cada 1 hora)
    echo "[$(date)] Ciclo legal completado. Esperando 1 hora para próxima verificación..." >> $LOG_FILE
    sleep 3600
done
