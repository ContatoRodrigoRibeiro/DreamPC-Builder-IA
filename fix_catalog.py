import pandas as pd

print("🔍 Carregando e limpando hardware_catalog.csv...")

df = pd.read_csv('data/hardware_catalog.csv')

# Remove colunas Unnamed
df = df.loc[:, ~df.columns.str.contains('^Unnamed')].copy()

# Nomeia colunas de forma limpa
df.columns = df.columns.str.strip()

# Mapeamento correto por categoria
name_map = {
    'CPU': 'Processador',
    'Video Card': 'Placa de vídeo',
    'Mother Board': 'Placa-mãe',
    'Storage': 'Armazenamento'
}

# Coluna de preço (pode ser Preço ou Preço PIX)
price_col = 'Preço' if 'Preço' in df.columns else 'Preço PIX'

# Cria as colunas padrão que o app precisa
df['PRODUCT_NAME'] = None
df['LIST_PRICE'] = None
df['DESCRIPTION'] = ''

for cat in df['CATEGORY_NAME'].unique():
    mask = df['CATEGORY_NAME'] == cat

    # Nome do produto
    if cat in name_map and name_map[cat] in df.columns:
        df.loc[mask, 'PRODUCT_NAME'] = df.loc[mask, name_map[cat]]

    # Preço
    if price_col in df.columns:
        preco_str = df.loc[mask, price_col].astype(str).str.replace('R$', '', regex=False) \
            .str.replace('.', '').str.replace(',', '.').str.strip()
        df.loc[mask, 'LIST_PRICE'] = pd.to_numeric(preco_str, errors='coerce')

    # Descrição simples
    df.loc[mask, 'DESCRIPTION'] = df.loc[mask, 'PRODUCT_NAME'].astype(str)

# Mantém só as colunas que o app usa
df = df[['CATEGORY_NAME', 'PRODUCT_NAME', 'LIST_PRICE', 'DESCRIPTION', 'LAST_UPDATE']].copy()

# Remove linhas sem nome ou preço
df = df.dropna(subset=['PRODUCT_NAME', 'LIST_PRICE'])

# Salva o arquivo limpo
df.to_csv('data/hardware_catalog.csv', index=False, encoding='utf-8')

print("\n🎉 CATÁLOGO LIMPO COM SUCESSO!")
print("Colunas finais:", df.columns.tolist())
print(f"Total de produtos: {len(df)}")
print(df.groupby('CATEGORY_NAME').size())