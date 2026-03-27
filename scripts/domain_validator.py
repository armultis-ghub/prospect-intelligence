import subprocess
import re
import socket
import json

# APIE v10.12 - Zero Token Domain Validator
# NDA P-20260325-DOMAIN

def get_dns_records(domain):
    """
    Obtiene registros TXT y MX usando comandos nativos del sistema.
    Busca evidencia de RNC o vinculación con la empresa.
    """
    try:
        # 1. Buscar registros TXT (donde a veces se colocan validaciones de propiedad o RNC)
        txt_records = subprocess.check_output(["dig", "+short", "TXT", domain], timeout=10).decode().splitlines()
        
        # 2. Verificar servidores de correo (MX)
        mx_records = subprocess.check_output(["dig", "+short", "MX", domain], timeout=10).decode().splitlines()
        
        return {"txt": txt_records, "mx": mx_records}
    except:
        return {"txt": [], "mx": []}

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.sentinel_reporter import report_error

def verify_email_server(email):
    # ... (lógica SMTP)
    except Exception as e:
        report_error(f"Validación de Correo: {email}", f"Fallo en Handshake SMTP: {str(e)}")
        return False
    """
    Verifica si el servidor de correo acepta el destinatario sin enviar el correo (SMTP VRFY/RCPT check).
    0 Tokens - Ejecución local.
    """
    domain = email.split('@')[1]
    try:
        # Obtener el servidor MX prioritario
        mx_out = subprocess.check_output(["dig", "+short", "MX", domain], timeout=10).decode().splitlines()
        if not mx_out: return False
        
        mx_server = sorted(mx_out, key=lambda x: int(x.split()[0]))[0].split()[1]
        
        # Intento de conexión SMTP básica (Handshake)
        # Esto confirma que el dominio tiene un servidor activo y configurado.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((mx_server, 25))
        s.recv(1024)
        s.send(b"HELO armultis.com\r\n")
        s.recv(1024)
        s.send(f"MAIL FROM:<jose.rondon@armultis.com>\r\n".encode())
        s.recv(1024)
        s.send(f"RCPT TO:<{email}>\r\n".encode())
        resp = s.recv(1024).decode()
        s.send(b"QUIT\r\n")
        s.close()
        
        # Si el servidor responde 250, el correo existe y es válido.
        return "250" in resp
    except:
        return False

def search_domain_locally(company_name, rnc):
    """
    Usa el motor Shadow (Playwright) para buscar en Google y extraer el dominio,
    luego valida propiedad mediante búsqueda de RNC en el HTML o DNS.
    """
    # Lógica: Google Search (Shadow) -> Hallar link -> Scrape HTML -> Buscar RNC en footer/legal.
    pass
