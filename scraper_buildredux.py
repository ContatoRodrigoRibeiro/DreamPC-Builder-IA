import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import os
import re


async def scrape_buildredux():
    print("🚀 Iniciando scraper do BuildRedux - Gaming Computers (versão definitiva com <grid-item>)...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        url = "https://www.buildredux.com/collections/gaming-computers"
        await page.goto(url, wait_until="networkidle", timeout=120000)
        print("✅ Página carregada")

        # Espera o elemento customizado <grid-item>
        await page.wait_for_selector("grid-item", timeout=90000)
        print("✅ Elementos <grid-item> detectados")

        # Scroll forte
        print("📜 Scroll agressivo...")
        for i in range(45):
            await page.evaluate("window.scrollBy(0, 2200)")
            await asyncio.sleep(1.4)
            if i % 8 == 0:
                print(f"   Scroll {i + 1}/45")

        # Pega todos os <grid-item>
        cards = await page.query_selector_all("grid-item")
        print(f"✅ Encontrados {len(cards)} cards de builds")

        data = []

        for card in cards:
            try:
                text = await card.inner_text()
                text = re.sub(r'\s+', ' ', text).strip()

                if not re.search(r'\$\d', text):
                    continue

                # Nome do build
                name = "Build sem nome"
                name_match = re.search(r'(Prime|Good|Better|Elite|Phoenix|Apex|Titan|Legend|Pro|Custom)[^$]*', text,
                                       re.I)
                if name_match:
                    name = name_match.group(0).strip()
                else:
                    # Pega o título
                    title = await card.query_selector("p.product-item__title")
                    if title:
                        name = await title.inner_text()

                # Preço
                price_match = re.search(r'R?\$[\s]*([\d.,]+)', text)
                price = float(price_match.group(1).replace(',', '')) if price_match else 0.0

                if price < 300:
                    continue

                data.append({
                    "BUILD_NAME": name[:120],
                    "TOTAL_PRICE": round(price, 2),
                    "CPU": "N/A",
                    "GPU": "N/A",
                    "RAM": "N/A",
                    "STORAGE": "N/A",
                    "MOTHERBOARD": "N/A",
                    "FULL_SPECS": text[:900],
                    "LAST_UPDATE": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "SOURCE": "BuildRedux"
                })

                print(f"   ✓ Extraído: {name[:70]}... → R$ {price:,.2f}")

            except:
                continue

        await browser.close()

    # Salva o CSV
    if data:
        df = pd.DataFrame(data)
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/buildredux_builds.csv", index=False, encoding="utf-8")

        print(f"\n🎉 SUCESSO! {len(df)} builds extraídos do BuildRedux")
        print(f"Arquivo salvo → data/buildredux_builds.csv")
        print("\nPreview:")
        print(df[['BUILD_NAME', 'TOTAL_PRICE']].head(15).to_string(index=False))
    else:
        print("❌ Nenhum build extraído.")


if __name__ == "__main__":
    asyncio.run(scrape_buildredux())