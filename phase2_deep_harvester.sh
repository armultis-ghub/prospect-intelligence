#!/bin/bash

# Aiara OSINT Deep Harvester - Phase 2
# NDA P-20260402-PH2
# Objetivo: Investigar todos los prospectos SUCCESS existentes en apie_v10.db sin tokens.

WORKSPACE="/root/.openclaw/workspace/github_projects/prospect-intelligence"
VENV="$WORKSPACE/venv/bin/python3"
LOG_FILE="$WORKSPACE/phase2_osint.log"

echo "[$(date)] >>> INICIANDO FASE 2: INVESTIGACIÓN PROFUNDA OSINT <<<" >> $LOG_FILE
echo "[$(date)] Objetivo: Barrido total de prospectos SUCCESS sin email real." >> $LOG_FILE

while true; do
    # Ajuste de Lote para Máxima Efectividad (2GB RAM + Human Simulation)
    # Lotes de 5 para evitar detección y saturación.
    echo "[$(date)] Iniciando ciclo de investigación (Lote de 5)..." >> $LOG_FILE
    
    # Ejecutar Harvester
    $VENV $WORKSPACE/osint_harvester.py --batch 5 >> $LOG_FILE 2>&1
    
    # Verificar progreso
    TOTAL_SUCCESS=$(sqlite3 $WORKSPACE/apie_v10.db "SELECT COUNT(*) FROM queue WHERE status = 'SUCCESS';")
    WITH_CONTACT=$(sqlite3 $WORKSPACE/apie_v10.db "SELECT COUNT(*) FROM queue WHERE status = 'SUCCESS' AND (real_email IS NOT NULL AND real_email != '');")
    REMAINING=$(($TOTAL_SUCCESS - $WITH_CONTACT))
    
    echo "[$(date)] Estado: $WITH_CONTACT/$TOTAL_SUCCESS investigados con éxito. Restantes: $REMAINING" >> $LOG_FILE
    
    if [ "$REMAINING" -le 0 ]; then
        echo "[$(date)] INVESTIGACIÓN TOTAL COMPLETADA." >> $LOG_FILE
        break
    fi

    # Pausa extendida para rotación de IP y evasión de bloqueos (Cero Tokens)
    # Entre 3 y 5 minutos para asegurar que Google no nos catalogue como bot.
    echo "[$(date)] Pausa de seguridad activa..." >> $LOG_FILE
    sleep $((180 + RANDOM % 120))
done
