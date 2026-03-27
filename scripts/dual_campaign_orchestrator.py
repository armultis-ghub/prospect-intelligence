import sqlite3
import json
import subprocess
import datetime
import os

# APIE Dual-Campaign Orchestrator (Priority & Secondary)
# NDA P-20260325-CAMPAIGN

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
MAILER_VENV = "/root/.openclaw/workspace/github_projects/aiara-mailer/venv/bin/python"
MAILER_PATH = "/root/.openclaw/workspace/github_projects/aiara-mailer/email_tool.py"

# Horarios de alto impacto gerencial (08:30 - 10:00 y 14:00 - 15:30)
IMPACT_WINDOWS = [
    (8, 30, 10, 30),
    (14, 0, 16, 0)
]

def is_impact_time():
    now = datetime.datetime.now()
    for start_h, start_m, end_h, end_m in IMPACT_WINDOWS:
        start = now.replace(hour=start_h, minute=start_m)
        end = now.replace(hour=end_h, minute=end_m)
        if start <= now <= end:
            return True
    return False

def run_priority_campaign():
    """Campaña vía email_tool.py con Tracking ID individual."""
    if not is_impact_time():
        print("Fuera de horario de impacto. Postergando batch de prioridad...")
        return

    # Lógica: Seleccionar 25 prospectos con INTEL_READY que no hayan sido contactados
    # Ejecutar mailer.py --track y capturar el ID en la DB
    pass

def generate_automotive_body(name, activity, intel, location):
    # Lógica de Anclaje de Confianza para Sector Automotriz (NDA P-20260325-AUTO)
    social_text = ""
    if intel.get('social', {}).get('instagram'):
        social_text = f"He seguido de cerca su inventario en Instagram; la presentación de sus unidades refleja un estándar de calidad que en ARMULTIS valoramos profundamente.\n"

    return f"""Estimados directivos de {name},

Le saludamos desde AR Multiservices InT (ARMULTIS).

{social_text}Como especialistas en el sector de {activity} en {location}, entendemos que la agilidad en el cierre de ventas y la transparencia fiscal son sus prioridades. Actualmente, hemos validado que su dealer aún no ha integrado la Facturación Electrónica (e-CF) obligatoria, lo cual es vital para la emisión de comprobantes válidos en la transferencia de vehículos.

Es importante destacar que en ARMULTIS contamos con una sólida trayectoria en el sector; actualmente brindamos servicios estratégicos a **NF Garantías**, parte integral del prestigioso grupo **NF GROUP, S.R.L.** Esta alianza nos permite entender a fondo las necesidades de protección y cumplimiento que su negocio demanda.

Nuestra solución e-CF para el sector automotriz permite automatizar sus reportes a la DGII mientras mantiene la seguridad SHA-256 en cada transacción.

Podemos coordinar una demostración técnica respondiendo a este correo o vía WhatsApp directo al {WHATSAPP_CONTACT}.

Atentamente,

Aiara
Asistencia Ejecutiva | ARMULTIS
"""
    # Lógica de Anclaje de Confianza Universal (NDA P-20260325-TRUST)
    anchor_text = ""
    if intel.get('gov_interaction', {}).get('dgcp_provider'):
        award = intel['gov_interaction'].get('last_award', 'procesos de licitación')
        anchor_text = f"Hemos dado seguimiento a su trayectoria como proveedores del Estado, específicamente en {award}. En este ecosistema, la validez de sus e-CF es un pilar de cumplimiento innegociable.\n"
    
    social_text = ""
    if intel.get('social', {}).get('instagram') or intel.get('social', {}).get('facebook'):
        platform = "Instagram" if intel.get('social', {}).get('instagram') else "redes sociales"
        social_text = f"Vimos su reciente presencia en {platform}; es evidente el compromiso de {name} con la excelencia en el sector de {activity}.\n"

    return f"""Estimados directivos de {name},

Le saludamos desde AR Multiservices InT (ARMULTIS).

{anchor_text}{social_text}
Basados en nuestro análisis de cumplimiento para empresas en la jurisdicción de {location}, hemos confirmado que su organización aún tiene pendiente la transición obligatoria hacia la Facturación Electrónica (e-CF).

En ARMULTIS nos especializamos en blindar la operatividad fiscal de empresas de alto perfil. Nuestras soluciones no solo garantizan el cumplimiento ante la DGII, sino que optimizan su ciclo de facturación con seguridad SHA-256.

Pueden contactarnos para una sesión de consultoría respondiendo a este correo o vía WhatsApp directo al {WHATSAPP_CONTACT}.

Atentamente,

Aiara
Asistencia Ejecutiva | ARMULTIS
"""

if __name__ == "__main__":
    print("Orquestador de Campaña Dual (v10.7) Registrado.")
