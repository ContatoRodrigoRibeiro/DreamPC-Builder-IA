import streamlit as st
import pandas as pd

st.set_page_config(page_title="DreamPC Builder IA", page_icon="🖥️", layout="wide")

st.title("🖥️ DreamPC Builder IA")
st.markdown("### Monte o PC dos sonhos usando dados reais do **MEUPC.NET**")

# ====================== CARREGAR CATÁLOGO ======================
@st.cache_data
def load_catalog():
    df = pd.read_csv('data/hardware_catalog.csv')
    return df

catalog_df = load_catalog()

# Debug: mostrar quantidade por categoria
counts = catalog_df['CATEGORY_NAME'].value_counts()
st.caption(f"📅 Última atualização: {catalog_df['LAST_UPDATE'].iloc[0]} | "
           f"CPU: {counts.get('CPU',0)} | Video Card: {counts.get('Video Card',0)} | "
           f"Mother Board: {counts.get('Mother Board',0)} | Storage: {counts.get('Storage',0)}")

# ====================== SIDEBAR ======================
st.sidebar.header("🎯 Seu PC dos Sonhos")

purpose = st.sidebar.selectbox(
    "Qual o principal uso do PC?",
    ["Gaming 1080p/1440p", "Gaming 4K / Streaming", "Edição de Vídeo / Render / 3D",
     "Trabalho / Multitarefa / Escritório", "Estudos / Uso Geral"]
)

budget = st.sidebar.slider("Orçamento máximo (R$)", 3000, 30000, 8500, step=500)

# ====================== IA - MONTAR PC (VERSÃO SEGURA) ======================
if st.sidebar.button("🚀 Montar PC dos Sonhos", type="primary", use_container_width=True):
    st.success("🔥 IA analisando o catálogo do MEUPC.NET...")

    allocation = {"CPU": 0.20, "Video Card": 0.48, "Mother Board": 0.10, "Storage": 0.22}
    if "Edição" in purpose or "Render" in purpose:
        allocation = {"CPU": 0.38, "Video Card": 0.35, "Mother Board": 0.10, "Storage": 0.17}
    elif not purpose.startswith("Gaming"):
        allocation = {"CPU": 0.25, "Video Card": 0.30, "Mother Board": 0.15, "Storage": 0.30}

    build = {}
    remaining_budget = budget

    for cat in ["CPU", "Video Card", "Mother Board", "Storage"]:
        cat_budget = int(remaining_budget * allocation[cat])
        items = catalog_df[catalog_df['CATEGORY_NAME'] == cat].copy()

        if items.empty:
            build[cat] = {"name": f"Sem {cat} no catálogo", "price": 0, "desc": "Rode o scraper novamente"}
            continue

        items = items.sort_values(by='LIST_PRICE')
        best_item = items[items['LIST_PRICE'] <= cat_budget]

        if not best_item.empty:
            chosen = best_item.iloc[-1]
        else:
            chosen = items.iloc[0]

        build[cat] = {
            "name": chosen['PRODUCT_NAME'],
            "price": chosen['LIST_PRICE'],
            "desc": chosen['DESCRIPTION']
        }
        remaining_budget -= chosen['LIST_PRICE']

    # ====================== EXIBIR ======================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("CPU")
        st.metric(build["CPU"]["name"], f"R$ {build['CPU']['price']:,.2f}".replace(",", "."))
        st.caption(build["CPU"]["desc"][:80] + "...")
    with col2:
        st.subheader("Placa de Vídeo")
        st.metric(build["Video Card"]["name"], f"R$ {build['Video Card']['price']:,.2f}".replace(",", "."))
        st.caption(build["Video Card"]["desc"][:80] + "...")
    with col3:
        st.subheader("Placa-Mãe")
        st.metric(build["Mother Board"]["name"], f"R$ {build['Mother Board']['price']:,.2f}".replace(",", "."))
        st.caption(build["Mother Board"]["desc"][:80] + "...")
    with col4:
        st.subheader("Armazenamento")
        st.metric(build["Storage"]["name"], f"R$ {build['Storage']['price']:,.2f}".replace(",", "."))
        st.caption(build["Storage"]["desc"][:80] + "...")

    total = sum(item["price"] for item in build.values())
    st.markdown(f"### 💰 **Total estimado: R$ {total:,.2f}**".replace(",", "."))

    if total <= budget:
        st.balloons()
        st.success("✅ Configuração perfeita!")
    else:
        st.warning("⚠️ Um pouco acima do orçamento.")

    st.divider()

# ====================== CATÁLOGO ======================
st.subheader("📦 Catálogo Completo do MEUPC.NET")
tab1, tab2, tab3, tab4 = st.tabs(["CPU", "Video Card", "Mother Board", "Storage"])
cols = ['PRODUCT_NAME', 'LIST_PRICE', 'DESCRIPTION']

with tab1: st.dataframe(catalog_df[catalog_df['CATEGORY_NAME'] == 'CPU'][cols], width='stretch', hide_index=True)
with tab2: st.dataframe(catalog_df[catalog_df['CATEGORY_NAME'] == 'Video Card'][cols], width='stretch', hide_index=True)
with tab3: st.dataframe(catalog_df[catalog_df['CATEGORY_NAME'] == 'Mother Board'][cols], width='stretch', hide_index=True)
with tab4: st.dataframe(catalog_df[catalog_df['CATEGORY_NAME'] == 'Storage'][cols], width='stretch', hide_index=True)