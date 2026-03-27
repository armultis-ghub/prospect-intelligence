import sys
import os
import datetime

# NDA P-20260317-054: Orquestador de Campaña Piloto Masiva e-CF
WORKSPACE_DIR = '/root/.openclaw/workspace'
sys.path.append(os.path.join(WORKSPACE_DIR, 'github_projects/ventax-incident-tool'))
from ventax_connector import _execute_kw, robust_write

def launch_pilot_campaign():
    print("--- Lanzando Primera Campaña Autónoma VentaX (Piloto) ---")
    
    # 1. Preparar el cuerpo del mensaje (HTML Estándar para VentaX)
    html_body = """
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2>URGENTE: Riesgo de Incumplimiento e-CF al 15 de Mayo</h2>
        <p>Estimado Director,</p>
        <p>Faltan pocas semanas para el plazo fatal dictado por la DGII. En <b>AR Multiservices InT.</b> hemos blindado la transición e-CF para Grandes Locales.</p>
        <p><b>Ventajas de VentaX Enterprise:</b></p>
        <ul>
            <li>Certificación e-CF Inmediata.</li>
            <li>Cumplimiento Ley 126-02 (Firma Digital).</li>
            <li>Automatización Financiera Total.</li>
        </ul>
        <p>¿Podemos agendar una breve sesión técnica de 10 minutos para asegurar su operación?</p>
        <p>Atentamente,<br><b>Aiara - Asistente de Estrategia</b><br>ARMULTIS</p>
    </div>
    """

    # 2. Crear la campaña en mailing.mailing
    campaign_payload = {
        'subject': 'URGENTE: Riesgo de Incumplimiento e-CF al 15 de Mayo',
        'body_html': html_body,
        'mailing_model_id': 10, # Normalmente res.partner o mailing.contact
        'state': 'draft',
        'mailing_type': 'mail'
    }
    
    mailing_id = _execute_kw('mailing.mailing', 'create', [campaign_payload])
    
    if mailing_id:
        print(f"[EXITO] Campaña Piloto creada en VentaX. ID: {mailing_id}")
        # En una ejecución real aquí se programaría el envío asíncrono
        return mailing_id
    return None

if __name__ == "__main__":
    launch_pilot_campaign()
