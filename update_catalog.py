import pandas as pd
import re

print("🔄 Atualizando catálogo com todas as informações técnicas...")

df = pd.read_csv('data/hardware_catalog.csv')


# Função robusta para extrair specs
def extract_specs(text):
    text = str(text)
    specs = {'Clock_GHz': None, 'Cores': None, 'TDP_W': None}

    # Clock (GHz)
    clock = re.search(r'Speed:?\s*([\d.]+)\s*GHz', text, re.I)
    if clock:
        specs['Clock_GHz'] = float(clock.group(1))

    # Cores
    cores = re.search(r'Cores:?\s*(\d+)', text, re.I)
    if cores:
        specs['Cores'] = int(cores.group(1))

    # TDP (Watts)
    tdp = re.search(r'TDP:?\s*(\d+)\s*W', text, re.I)
    if tdp:
        specs['TDP_W'] = int(tdp.group(1))

    return specs


# Aplica a extração
extracted = df['DESCRIPTION'].apply(extract_specs)
df['Clock_GHz'] = extracted.apply(lambda x: x['Clock_GHz'])
df['Cores'] = extracted.apply(lambda x: x['Cores'])
df['TDP_W'] = extracted.apply(lambda x: x['TDP_W'])

# Formata preço em Real brasileiro
df['Preço'] = df['LIST_PRICE'].apply(
    lambda x: f"R$ {float(x):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

print("✅ Colunas criadas:")
print(df[['CATEGORY_NAME', 'PRODUCT_NAME', 'Clock_GHz', 'Cores', 'TDP_W']].head())

df.to_csv('data/hardware_catalog.csv', index=False, encoding='utf-8')
print("🎉 hardware_catalog.csv atualizado com sucesso!")