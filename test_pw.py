import asyncio
from playwright.async_api import async_playwright
import sys

async def run():
    print("Testing Playwright...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            print("Navigating to DGII...")
            await page.goto("https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/rnc.aspx", timeout=30000)
            title = await page.title()
            print(f"Page Title: {title}")
            await browser.close()
            print("Test Success")
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())
