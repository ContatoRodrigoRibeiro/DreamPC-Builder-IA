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
    await page.goto(url, wait_until="networkidle", timeout=90000)

    # Espera a tabela carregar
    await page.wait_for_selector("table", timeout=60000)
    print("✅ Tabela carregada!")

    # Scroll para carregar todos os produtos
    for _ in range(15):
        await page.evaluate("window.scrollBy(0, 5000)")
        await asyncio.sleep(1.5)

    html = await page.content()
    tables = pd.read_html(html)

    if not tables:
        print("❌ Nenhuma tabela encontrada")
        return []

    df_table = tables[0]
    print(f"✅ Tabela com {len(df_table)} linhas detectada")

    products = []
    for _, row in df_table.iterrows():
        try:
            name = str(row.iloc[1]) if pd.notna(row.iloc[1]) else str(row.iloc[0])
            # Ajuste fino para nome do produto
            if len(name) < 15 and "GHz" in name:
                name = str(row.iloc[2])

            # Extrai preço
            price = None
            for col in row.index:
                cell = str(row[col])
                if "R$" in cell:
                    clean_price = ''.join(filter(str.isdigit, cell.replace(',', '.')))
                    price = float(clean_price) / 100
                    break

            if price is None or price < 10:
                continue

            # Descrição
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

    print(f"✅ Extraídos {len(products)} produtos de {category_name}")
    return products


async def main():
    os.makedirs("data", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # False = você vê o navegador
        page = await browser.new_page()

        all_products = []
        for cat_name, url in CATEGORIES.items():
            products = await scrape_category(page, cat_name, url)
            all_products.extend(products)

        await browser.close()

    if not all_products:
        print("❌ Nenhum produto extraído. Site mudou?")
        return

    df = pd.DataFrame(all_products)
    df = df.sort_values(by=["CATEGORY_NAME", "LIST_PRICE"]).reset_index(drop=True)
    df.to_csv("data/hardware_catalog.csv", index=False, encoding="utf-8")

    print("\n🎉 CATÁLOGO ATUALIZADO COM SUCESSO!")
    print(f"Total de produtos: {len(df)}")
    print(f"Arquivo salvo: data/hardware_catalog.csv")


if __name__ == "__main__":
    asyncio.run(main())