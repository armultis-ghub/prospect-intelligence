# MANUAL_OFFLINE.md - Prospect Intelligence (APIE)

## Manual de Uso
El sistema opera de forma autónoma mediante orquestadores en segundo plano. Sin embargo, puede ser controlado manualmente para tareas específicas.

### Ejecución de Prospección (DGII)
Para lanzar un batch manual de investigación:
```bash
/root/.openclaw/workspace/github_projects/prospect-intelligence/venv/bin/python3 \
/root/.openclaw/workspace/github_projects/prospect-intelligence/dgii_module_v10.py --batch <CANTIDAD>
```

### Ejecución del Pipeline Unificado (OSINT/MX)
Para validar contactos de prospectos ya calificados:
```bash
/root/.openclaw/workspace/github_projects/prospect-intelligence/venv/bin/python3 \
/root/.openclaw/workspace/github_projects/prospect-intelligence/scripts/unified_sentinel_pipeline.py
```

### Ejecución del Orquestador Relentless (Modo Guardian)
Para iniciar el ciclo infinito con prioridad Noviembre:
```bash
nohup /root/.openclaw/workspace/github_projects/prospect-intelligence/relentless_orchestrator_v11.sh > \
/root/.openclaw/workspace/github_projects/prospect-intelligence/orchestrator_v11.log 2>&1 &
```

## Ubicación y Manejo de Logs
Los logs están segmentados por función para facilitar la auditoría:

1. **Log de Actividad Diaria:** `prospeccion_diaria.log`
   - Detalle segundo a segundo de cada RNC procesado (SUCCESS/FAILED).
2. **Log del Pipeline Unificado:** `unified_guardian.log`
   - Registro de validaciones MX, hallazgos OSINT y reportes enviados.
3. **Log del Orquestador:** `orchestrator_v11.log`
   - Estado de los ciclos de batch y conteo de pendientes.
4. **Logs Históricos:** `apie_background_v10.log`
   - Salida técnica bruta del motor APIE.

**Manejo:** Se recomienda revisar `prospeccion_diaria.log` para monitorear el avance y `unified_guardian.log` para confirmar la integridad de los correos obtenidos.
