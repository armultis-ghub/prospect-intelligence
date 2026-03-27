# PLAN_DE_ACCION.md - Prospect Intelligence (APIE)

## Visión General
Prospect Intelligence (APIE) es el motor central de generación de demanda de ARMULTIS. Su objetivo es identificar, calificar y validar prospectos del mercado dominicano mediante la integración de fuentes gubernamentales (DGII) e inteligencia de fuentes abiertas (OSINT). El sistema está diseñado bajo el ADN CID (Confidencialidad, Integridad y Disponibilidad), asegurando que cada contacto sea veraz y de alto valor estratégico.

## Alcance Técnico
1. **Extracción DGII:** Consulta automatizada de RNCs para obtener Razón Social, Estado y Actividad Económica.
2. **Segmentación Estratégica:** Clasificación automática en categorías:
   - `VENTAX_MIPYMES`: Sin Facturación Electrónica.
   - `AI_CHATBOT_UPSKLLING`: Sectores prioritarios para IA.
   - `CYBERSEC_PBX_AUDIT`: Prospectos para servicios avanzados de seguridad y VoIP.
3. **Pipeline Unificado (v14+):** Ejecución consecutiva de Dorking, Social Discovery, PDF Metadata y WHOIS.
4. **MX Guardian:** Validación técnica mandatoria de registros MX y Handshake SMTP para eliminar dominios huérfanos.
5. **Orquestación Relentless:** Ciclos continuos de procesamiento con prioridad para registros de noviembre.
6. **Sistema de Alertas:** Notificaciones duales (Correo Prioritario + WhatsApp Secundario).

## Detalles Relacionados
- **Base de Datos:** SQLite (`apie_v10.db`) con cache semántico de dominios.
- **ADN CID:** Cada bit de información es validado bit-a-bit antes de ser reportado.
- **Ahorro de Tokens:** Lógica computacional local predominante sobre consultas a LLMs.
