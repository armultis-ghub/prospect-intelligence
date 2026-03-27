# Aiara Prospect-Intelligence Engine (APIE) - V2.0 EXTENDED (NDA P-20260324-002)

## 1. Visión General
APIE se consolida como el motor central de inteligencia de ARMULTIS, absorbiendo las capacidades avanzadas de `prospector-engine` para dominar el mercado dominicano mediante automatización determinista y análisis multicanal.

## 2. Nuevas Capacidades Integradas (Upgrade V2.0)
- **Módulo Omnicanal:** Capacidad de búsqueda extendida en Instagram, Facebook y Páginas Amarillas para capturar WhatsApp Business y perfiles comerciales (0 tokens).
- **Priorizador de Transparencia:** Clasificación automática de prospectos B2G (vendedores al estado) mediante análisis de razón social (Constructoras, Ingeniería, Suministros).
- **Importador DGII Robusto:** Procesamiento automático de listados oficiales con manejo de encoding latin-1 y normalización de RNC.
- **Orquestador de Campañas Piloto:** Capacidad de inyectar campañas directamente en `mailing.mailing` de VentaX con optimización de tiempos de envío (Horario Prime).

## 3. Integración en el Protocolo 25
La mejora se inserta en la **Fase 4.1 (Sigilosa)** y **Fase 5 (Inteligencia)**:
1. **Dorking Extendido:** Antes de la Carga 4, se ejecutan queries multicanal (FB/IG/Páginas Amarillas).
2. **Scoring de Prioridad:** Los leads en VentaX reciben etiquetas de prioridad basadas en su potencial B2G.
3. **Automatización de Seguimiento:** Preparación de lotes para el Motor de Campañas de VentaX.

## 4. Eficiencia y Token Guard
- **95% de la ejecución es local (Python):** El consumo de tokens se limita exclusivamente al cruce semántico final de Aiara.
- **PTC Cumplido:** Cada registro en VentaX llevará el metadato de la fuente de captura original (#LinkedIn, #OSINT_RD, #DGII).

---
*Aprobado por Jose Rondon - 2026-03-24 10:46 AST*
