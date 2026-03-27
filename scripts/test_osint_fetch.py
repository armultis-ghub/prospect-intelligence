import asyncio
import sys
import os
import random
from playwright.async_api import async_playwright

sys.path.append('/root/.openclaw/workspace/github_projects/prospect-intelligence/')
from dgii_module_v10 import APIE_Engine_V10_3

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        engine = APIE_Engine_V10_3()
        context = await browser.new_context(
            user_agent=random.choice(engine.user_agents),
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()
        
        # Probar con los 3 prospectos
        targets = [
            ("101107962", "REPUESTOS MOTOCAR SRL"),
            ("101869951", "LOS MARLINS SUITES HOTEL S A"),
            ("130045518", "PRIEGO COMERCIAL SRL")
        ]
        
        for rnc, name in targets:
            print(f"Buscando {rnc} ({name})...")
            res = await engine.fetch(rnc, page)
            print(f"Resultado: {res}")
            await asyncio.sleep(5)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
