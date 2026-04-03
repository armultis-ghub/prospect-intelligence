import sqlite3
import json
import time
import re
import os
import random
import asyncio
import argparse
from playwright.async_api import async_playwright

# Aiara OSINT Module v1.0 - "The Ghost Harvester"
# Objetivo: Prospección OSINT sin uso de tokens vía Google Dorking y extracción directa.

DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"

class OSINT_Harvester:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]

    def extract_contacts(self, text):
        # Regex para Emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        # Regex para WhatsApp / Teléfonos RD (809, 829, 849)
        phones = re.findall(r'(?:809|829|849)[-\s\.]?\d{3}[-\s\.]?\d{4}', text)
        
        # Limpieza básica
        emails = list(set([e.lower() for e in emails if not e.lower().endswith(('.png', '.jpg', '.gif', 'wixpress.com'))]))
        phones = list(set([p.replace('-', '').replace(' ', '').replace('.', '') for p in phones]))
        
        return emails, phones

    async def google_dork(self, query, page):
        contacts = {"emails": [], "phones": []}
        try:
            print(f"      [OSINT] Ejecutando Dork: {query[:50]}...")
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=20"
            
            # Simular comportamiento humano: Pausa pre-navegación
            await asyncio.sleep(random.uniform(1, 3))
            
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            
            # Verificar si caímos en un CAPTCHA
            if "detected unusual traffic" in await page.content():
                print("      [ALERTA] Google ha detectado tráfico inusual. Rotando sesión...")
                return "RECAPTCHA"

            results = await page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('div.g'));
                return links.map(l => ({
                    title: l.querySelector('h3')?.innerText,
                    url: l.querySelector('a')?.href,
                    snippet: l.innerText
                }));
            }""")

            if not results:
                # Intento de selector alternativo para resultados
                results = await page.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll('a h3')).map(h => h.closest('a'));
                    return links.map(l => ({
                        title: l.innerText,
                        url: l.href,
                        snippet: l.parentElement.innerText
                    }));
                }""")

            for res in results:
                # 1. Extracción de snippets (Ahorra navegación, 0 tokens, alta velocidad)
                e, p = self.extract_contacts(res.get('snippet', ''))
                contacts["emails"].extend(e)
                contacts["phones"].extend(p)

                # 2. Navegación profunda solo si el snippet no dio resultados y el sitio es prioritario
                if (not contacts["emails"] or not contacts["phones"]) and res.get('url'):
                    if any(x in res['url'] for x in ['.do', 'instagram.com', 'facebook.com', 'maptons.com', 'paginasamarillas.com.do']):
                        try:
                            await page.goto(res['url'], wait_until="domcontentloaded", timeout=15000)
                            content = await page.content()
                            e, p = self.extract_contacts(content)
                            contacts["emails"].extend(e)
                            contacts["phones"].extend(p)
                        except:
                            continue
            
            return contacts
        except Exception as e:
            print(f"      [OSINT-ERROR] {e}")
            return contacts

async def process_osint(batch_size=10):
    harvester = OSINT_Harvester()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(harvester.user_agents))
        page = await context.new_page()

        conn = sqlite3.connect(DB_PATH)
        # PRIORIDAD MÁXIMA: Prospectos SUCCESS que NO son facturadores electrónicos (VENTAX_MIPYMES)
        # Y que no han sido investigados (real_email IS NULL o vacío)
        cursor = conn.execute("""
            SELECT rnc, razon_social, nombre_comercial FROM queue 
            WHERE status = 'SUCCESS' 
            AND (real_email IS NULL OR real_email = '')
            ORDER BY CASE WHEN category = 'VENTAX_MIPYMES' THEN 0 ELSE 1 END, last_update DESC
            LIMIT ?
        """, (batch_size,))
        
        prospects = cursor.fetchall()
        
        for rnc, razon_social, nombre_comercial in prospects:
            print(f"\n[OSINT] Iniciando investigación profunda para: {razon_social} (RNC: {rnc})")
            
            # Definir Dorks según estructura solicitada
            name_query = f'"{razon_social}"'
            if nombre_comercial and nombre_comercial != razon_social:
                name_query += f' OR "{nombre_comercial}"'
            
            dorks = [
                f'{name_query} OR "{rnc}" site:.do (whatsapp OR "wa.me" OR "809" OR "829" OR "849" OR "@" OR correo OR email)',
                f'{name_query} OR "{rnc}" site:.do (filetype:pdf OR filetype:xls OR filetype:xlsx OR filetype:doc) (whatsapp OR "809" OR "@" OR email)',
                f'{name_query} site:instagram.com OR site:facebook.com (whatsapp OR "809" OR "@" OR email)'
            ]

            all_emails = []
            all_phones = []

            for dork in dorks:
                res = await harvester.google_dork(dork, page)
                all_emails.extend(res["emails"])
                all_phones.extend(res["phones"])
                await asyncio.sleep(random.uniform(2, 5)) # Delay anti-bot

            # Consolidar
            unique_emails = list(set(all_emails))
            unique_phones = list(set(all_phones))
            
            # Seleccionar el mejor email (no genérico si es posible)
            best_email = None
            if unique_emails:
                # Priorizar correos que NO empiecen con info, ventas, etc.
                personal = [e for e in unique_emails if not any(x in e for x in ['info@', 'ventas@', 'admin@', 'recepcion@'])]
                best_email = personal[0] if personal else unique_emails[0]
            
            # --- MEJORA: Marcar como INVESTIGADO incluso si no hay resultados ---
            final_email = best_email if best_email else "NOT_FOUND"
            
            osint_summary = {
                "harvest_date": time.strftime('%Y-%m-%d'),
                "all_emails": unique_emails,
                "all_phones": unique_phones,
                "source": "Aiara OSINT Engine V1",
                "found_results": True if (unique_emails or unique_phones) else False
            }
            
            conn.execute("""
                UPDATE queue 
                SET real_email = ?, osint_data = ?, last_update = CURRENT_TIMESTAMP
                WHERE rnc = ?
            """, (final_email, json.dumps(osint_summary), rnc))
            conn.commit()

            # --- NUEVO: Log de Captura Maestro (Texto Plano) ---
            if unique_emails or unique_phones:
                log_file = "/root/.openclaw/workspace/github_projects/prospect-intelligence/master_contacts.log"
                with open(log_file, "a") as f:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{timestamp}] ENTIDAD: {razon_social} | RNC: {rnc}\n")
                    if unique_emails:
                        f.write(f"   EMAILS: {', '.join(unique_emails)}\n")
                    if unique_phones:
                        f.write(f"   PHONES: {', '.join(unique_phones)}\n")
                    f.write("-" * 50 + "\n")
            
            print(f"   [RESULTADO] Emails: {len(unique_emails)} | Phones: {len(unique_phones)}")
            if best_email: print(f"   [CAPTURADO] {best_email}")

        conn.close()
        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=int, default=5)
    args = parser.parse_args()
    
    asyncio.run(process_osint(args.batch))
