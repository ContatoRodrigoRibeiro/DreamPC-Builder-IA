import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import os
from io import StringIO

CATEGORIES = {
    "CPU": "https://meupc.net/processadores",
    "Video Card": "https://meupc.net/placas-video",
    "Mother Board": "https://meupc.net/placas-mae",
    "Storage": "https://meupc.net/armazenamentos",
}


async def scrape_category(page, category_name, url):
    print(f"🔍 Scraping {category_name} → {url}")
    await page.goto(url, wait_until="networkidle", timeout=90000)
    await page.wait_for_selector("table", timeout=60000)

    for i in range(25):
        await page.evaluate("window.scrollBy(0, 3000)")
        await asyncio.sleep(1.2)
        if i % 8 == 0:
            print(f"   Scroll {i + 1}/25 para {category_name}")

    html = await page.content()
    tables = pd.read_html(StringIO(html))  # <-- Correção do warning

    if not tables:
        print(f"   ❌ Nenhuma tabela em {category_name}")
        return pd.DataFrame()

    df = tables[0].copy()
    df['CATEGORY_NAME'] = category_name
    df['LAST_UPDATE'] = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"   ✅ {len(df)} produtos encontrados em {category_name}")
    return df


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        all_dfs = []
        for cat_name, url in CATEGORIES.items():
            df_cat = await scrape_category(page, cat_name, url)
            if not df_cat.empty:
                all_dfs.append(df_cat)

        await browser.close()

        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            os.makedirs("data", exist_ok=True)
            final_df.to_csv("data/hardware_catalog.csv", index=False, encoding="utf-8")
            print("\n🎉 CATÁLOGO GERADO COM SUCESSO!")
            print(final_df.groupby('CATEGORY_NAME').size())
        else:
            print("❌ Nenhum dado foi extraído.")


if __name__ == "__main__":
    asyncio.run(main())