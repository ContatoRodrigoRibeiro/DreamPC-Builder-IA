import pandas as pd
import re

print("🔄 Atualizando catálogo com specs técnicas...")

df = pd.read_csv('data/hardware_catalog.csv')


# Função para extrair dados da coluna DESCRIPTION
def extract_specs(text):
    text = str(text)
    specs = {}

    # Clock / Speed (GHz)
    clock_match = re.search(r'Speed:?\s*([\d.]+)\s*GHz', text, re.I)
    specs['Clock_GHz'] = float(clock_match.group(1)) if clock_match else None

    # Cores
    cores_match = re.search(r'Cores:?\s*(\d+)', text, re.I)
    specs['Cores'] = int(cores_match.group(1)) if cores_match else None

    # TDP (Watts)
    tdp_match = re.search(r'TDP:?\s*(\d+)\s*W', text, re.I)
    specs['TDP_W'] = int(tdp_match.group(1)) if tdp_match else None

    return specs


# Aplica a extração
extracted = df['DESCRIPTION'].apply(extract_specs)
df['Clock_GHz'] = extracted.apply(lambda x: x.get('Clock_GHz'))
df['Cores'] = extracted.apply(lambda x: x.get('Cores'))
df['TDP_W'] = extracted.apply(lambda x: x.get('TDP_W'))

# Formata preço brasileiro
df['Preço'] = df['LIST_PRICE'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

print(f"✅ Catálogo atualizado! Colunas novas: Clock_GHz, Cores, TDP_W")
print(df[['CATEGORY_NAME', 'PRODUCT_NAME', 'Preço', 'Clock_GHz', 'Cores', 'TDP_W']].head())

df.to_csv('data/hardware_catalog.csv', index=False, encoding='utf-8')
print("🎉 Arquivo hardware_catalog.csv atualizado com sucesso!")