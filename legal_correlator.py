import asyncio
import random
import sqlite3
import json
import time
import re
from playwright.async_api import async_playwright

# Aiara Legal Sentinel v1.0 - Reconsideration Correlation
# Objetivo: Identificar prospectos con historiales de reconsideración en DGII para venta forzada de e-CF.

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"
RECONSIDERATION_URL = "https://dgii.gov.do/legislacion/reconsideracion/Paginas/default.aspx"

async def fetch_reconsideration_indices():
    """Extrae los links de los PDFs de reconsideración de la DGII."""
    indices = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print(f"[LEGAL] Accediendo a portal de reconsideraciones...")
            await page.goto(RECONSIDERATION_URL, timeout=60000)
            
            # Buscar todos los enlaces que parezcan ser PDFs o resoluciones
            links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a'))
                    .filter(a => a.href.includes('.pdf') || a.href.includes('Resolucion'))
                    .map(a => ({ text: a.innerText, url: a.href }));
            }""")
            indices = links
        except Exception as e:
            print(f"[LEGAL-ERROR] No se pudo acceder al portal: {e}")
        await browser.close()
    return indices

async def correlate_prospects():
    conn = sqlite3.connect(DB_PATH)
    # PRIORIDAD: Solo SUCCESS que aún no han sido analizados legalmente (legal_issues es NULL o no existe en JSON)
    cursor = conn.execute("SELECT rnc, razon_social, osint_data FROM queue WHERE status = 'SUCCESS'")
    prospects = cursor.fetchall()
    
    indices = await fetch_reconsideration_indices()
    
    if not indices:
        print("[LEGAL] No se encontraron documentos para correlacionar.")
        return

    print(f"[LEGAL] Correlacionando {len(prospects)} prospectos contra {len(indices)} documentos legales...")
    
    matches_found = 0
    for rnc, name, osint_data in prospects:
        # Saltar si ya tiene análisis legal reciente para ahorrar recursos (0 tokens)
        osint_dict = json.loads(osint_data) if osint_data else {}
        if 'legal_issues' in osint_dict:
            continue

        rnc_clean = rnc.replace('-', '')
        found_in = []
        # Búsqueda ultra-rápida en memoria sin llamadas a APIs
        for doc in indices:
            if rnc_clean in doc['url'] or rnc in doc['url']:
                found_in.append(doc)
        
        # Marcar como analizado siempre para evitar re-procesamiento (Persistence 0 tokens)
        osint_dict['legal_issues'] = {
            "has_reconsiderations": True if found_in else False,
            "count": len(found_in),
            "last_check": time.strftime('%Y-%m-%d'),
            "source_url": RECONSIDERATION_URL,
            "docs": found_in[:5]
        }
        
        conn.execute("UPDATE queue SET osint_data = ? WHERE rnc = ?", (json.dumps(osint_dict), rnc))
        conn.commit()
        if found_in: matches_found += 1

    conn.close()
    print(f"[LEGAL] Proceso terminado localmente. {matches_found} correlaciones encontradas.")

if __name__ == "__main__":
    asyncio.run(correlate_prospects())
