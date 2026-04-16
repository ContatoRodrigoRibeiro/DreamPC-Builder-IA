import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import os

CATEGORIES = {
    "CPU": "https://meupc.net/processadores",
    "Video Card": "https://meupc.net/placas-video",
    "Mother Board": "https://meupc.net/placas-mae",
    "Storage": "https://meupc.net/armazenamentos",
}


async def scrape_category(page, category_name, url):
    print(f"🔍 Buscando {category_name} → {url}")
    await page.goto(url, wait_until="networkidle", timeout=120000)

    # Espera mais robusta pela tabela
    await page.wait_for_selector("table", timeout=60000)
    print(f"✅ Tabela de {category_name} carregada!")

    # Scroll mais agressivo (especialmente importante para Storage)
    for i in range(20):
        await page.evaluate("window.scrollBy(0, 6000)")
        await asyncio.sleep(1.8)
        if i % 5 == 0:
            print(f"   Scroll {i + 1}/20 em {category_name}...")

    html = await page.content()
    tables = pd.read_html(html)

    if not tables:
        print(f"❌ Nenhuma tabela encontrada em {category_name}")
        return []

    df_table = tables[0]
    print(f"✅ Tabela com {len(df_table)} linhas detectada em {category_name}")

    products = []
    for _, row in df_table.iterrows():
        try:
            name = str(row.iloc[1]) if pd.notna(row.iloc[1]) else str(row.iloc[0])
            if len(name.strip()) < 10:
                name = str(row.iloc[2])

            # Extrai preço
            price = None
            for col in row.index:
                cell = str(row[col])
                if "R$" in cell:
                    clean = ''.join(filter(str.isdigit, cell.replace(',', '.')))
                    price = float(clean) / 100
                    break

            if price is None or price < 10:
                continue

            desc = " | ".join([str(row[col]) for col in row.index[2:8] if pd.notna(row[col])])

            products.append({
                "CATEGORY_NAME": category_name,
                "PRODUCT_NAME": name.strip(),
                "LIST_PRICE": round(price, 2),
                "DESCRIPTION": desc.strip(),
                "LAST_UPDATE": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        except:
            continue

    print(f"✅ Extraídos {len(products)} produtos válidos de {category_name}")
    return products


async def main():
    os.makedirs("data", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        all_products = []
        for cat_name, url in CATEGORIES.items():
            products = await scrape_category(page, cat_name, url)
            all_products.extend(products)

        await browser.close()

    if not all_products:
        print("❌ Nenhum produto extraído.")
        return

    df = pd.DataFrame(all_products)
    df = df.sort_values(by=["CATEGORY_NAME", "LIST_PRICE"]).reset_index(drop=True)
    df.to_csv("data/hardware_catalog.csv", index=False, encoding="utf-8")

    print("\n🎉 CATÁLOGO ATUALIZADO COM SUCESSO!")
    print(f"Total de produtos: {len(df)}")
    print(f"Arquivo salvo: data/hardware_catalog.csv")


if __name__ == "__main__":
    asyncio.run(main())