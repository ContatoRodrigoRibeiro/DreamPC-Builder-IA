import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="DreamPC Builder IA", page_icon="🖥️", layout="wide")

st.title("🖥️ DreamPC Builder IA")
st.markdown("### A IA que entende o que você quer + Comparador de Peças")


# ====================== CARREGAR DADOS ======================
@st.cache_data
def load_data():
    meupc = pd.read_csv('data/hardware_catalog.csv')
    buildredux = pd.read_csv('data/buildredux_builds.csv')
    return meupc, buildredux


catalog_df, buildredux_df = load_data()

# ====================== TABS ======================
tab_builder, tab_comparator, tab_catalog = st.tabs(["🚀 Builder IA", "🔄 Comparar Peças", "📦 Catálogo Completo"])

# ====================== TAB 1 - BUILDER IA ======================
with tab_builder:
    st.subheader("✍️ Descreva o PC dos seus sonhos (com orçamento)")

    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    prompt = st.text_area(
        "Descreva o PC dos seus sonhos",
        value=st.session_state.prompt,
        placeholder="Ex: Quero um pc para estudar de até R$16000,00 ou um gamer bom para 1440p com 8500 reais...",
        height=130,
        label_visibility="collapsed"
    )

    st.session_state.prompt = prompt

    st.markdown("**Sugestões rápidas:**")
    col_sug = st.columns(5)
    examples = [
        "Gaming 1080p/1440p",
        "Gaming 4K / Streaming",
        "Edição de Vídeo / Render / 3D",
        "Trabalho / Multitarefa / Escritório",
        "Estudos / Uso Geral"
    ]

    for i, ex in enumerate(examples):
        with col_sug[i]:
            if st.button(ex, width='stretch', key=f"ex_{i}"):
                st.session_state.prompt = ex
                st.rerun()

    if st.button("🚀 Montar PC dos Sonhos com IA", type="primary", width='stretch'):
        if not st.session_state.prompt.strip():
            st.warning("Digite uma descrição ou escolha uma sugestão!")
            st.stop()

        st.success("🔥 IA analisando seu prompt + BuildRedux + MEUPC.NET...")

        prompt_lower = st.session_state.prompt.lower()

        budget_match = re.search(r'(?:até|orçamento|de|até r\$|r\$)\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:[.,]\d{2})?',
                                 prompt_lower)
        budget = int(budget_match.group(1).replace('.', '').replace(',', '')) if budget_match else 8500

        if any(k in prompt_lower for k in ["gamer", "gaming", "jogos", "1440", "1080"]):
            allocation = {"CPU": 0.22, "Video Card": 0.48, "Mother Board": 0.10, "Storage": 0.20}
        elif any(k in prompt_lower for k in ["4k", "streaming", "stream"]):
            allocation = {"CPU": 0.25, "Video Card": 0.50, "Mother Board": 0.10, "Storage": 0.15}
        elif any(k in prompt_lower for k in ["edição", "vídeo", "render", "3d", "photoshop", "premiere"]):
            allocation = {"CPU": 0.38, "Video Card": 0.35, "Mother Board": 0.12, "Storage": 0.15}
        elif any(k in prompt_lower for k in ["trabalho", "escritório", "multitarefa", "produtividade"]):
            allocation = {"CPU": 0.30, "Video Card": 0.25, "Mother Board": 0.15, "Storage": 0.30}
        else:
            allocation = {"CPU": 0.28, "Video Card": 0.32, "Mother Board": 0.15, "Storage": 0.25}

        build_match = None
        if not buildredux_df.empty:
            buildredux_df['TOTAL_PRICE_BRL'] = buildredux_df['TOTAL_PRICE'] * 5.30
            filtered = buildredux_df[buildredux_df['TOTAL_PRICE_BRL'] <= budget * 1.2].copy()
            if not filtered.empty:
                filtered['diff'] = abs(filtered['TOTAL_PRICE_BRL'] - budget)
                build_match = filtered.sort_values('diff').iloc[0]

        build = {}
        remaining = budget

        for cat in ["CPU", "Video Card", "Mother Board", "Storage"]:
            cat_budget = int(remaining * allocation[cat])
            items = catalog_df[catalog_df['CATEGORY_NAME'] == cat].copy()

            if items.empty:
                build[cat] = {"name": f"Sem {cat} disponível", "price": 0, "desc": ""}
                continue

            items = items.sort_values(by='LIST_PRICE')
            best = items[items['LIST_PRICE'] <= cat_budget]
            chosen = best.iloc[-1] if not best.empty else items.iloc[0]

            build[cat] = {
                "name": chosen['PRODUCT_NAME'],
                "price": chosen['LIST_PRICE'],
                "desc": chosen.get('DESCRIPTION', '')[:100]
            }
            remaining -= chosen['LIST_PRICE']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.subheader("CPU")
            st.metric(build["CPU"]["name"], f"R$ {build['CPU']['price']:,.2f}".replace(",", "."))
            st.caption(build["CPU"]["desc"])

        with col2:
            st.subheader("Placa de Vídeo")
            st.metric(build["Video Card"]["name"], f"R$ {build['Video Card']['price']:,.2f}".replace(",", "."))
            st.caption(build["Video Card"]["desc"])

        with col3:
            st.subheader("Placa-Mãe")
            st.metric(build["Mother Board"]["name"], f"R$ {build['Mother Board']['price']:,.2f}".replace(",", "."))
            st.caption(build["Mother Board"]["desc"])

        with col4:
            st.subheader("Armazenamento")
            st.metric(build["Storage"]["name"], f"R$ {build['Storage']['price']:,.2f}".replace(",", "."))
            st.caption(build["Storage"]["desc"])

        total = sum(item["price"] for item in build.values())
        st.markdown(f"### 💰 **Total estimado: R$ {total:,.2f}**".replace(",", "."))

        if build_match is not None:
            st.success(
                f"💡 **Inspirado no BuildRedux**: {build_match['BUILD_NAME']} (R$ {build_match['TOTAL_PRICE_BRL']:,.2f})")

        if total <= budget:
            st.balloons()
            st.success("✅ Configuração perfeita dentro do orçamento!")
        else:
            st.warning("⚠️ Um pouco acima do orçamento.")

# ====================== TAB 2 - COMPARADOR DE PEÇAS ======================
with tab_comparator:
    st.subheader("🔄 Comparador de Peças")

    col1, col2 = st.columns([1, 3])
    with col1:
        categoria = st.selectbox("Escolha a categoria", ["CPU", "Video Card", "Mother Board", "Storage"])

    produtos_categoria = catalog_df[catalog_df['CATEGORY_NAME'] == categoria].copy()

    with col2:
        produtos_selecionados = st.multiselect(
            "Selecione até 4 produtos para comparar",
            options=produtos_categoria['PRODUCT_NAME'].tolist(),
            max_selections=4,
            placeholder="Escolha os produtos..."
        )

    if st.button("Comparar Produtos", type="primary", width='stretch') and len(produtos_selecionados) >= 2:
        df_compare = produtos_categoria[produtos_categoria['PRODUCT_NAME'].isin(produtos_selecionados)].copy()
        df_compare['Preço'] = df_compare['LIST_PRICE'].apply(
            lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        compare_table = df_compare[['PRODUCT_NAME', 'Preço', 'DESCRIPTION']].set_index('PRODUCT_NAME').T
        st.dataframe(compare_table, width='stretch', hide_index=False)
    elif len(produtos_selecionados) >= 2:
        st.info("Clique no botão acima para gerar a comparação.")
    else:
        st.info("Selecione pelo menos 2 produtos para comparar.")

# ====================== TAB 3 - CATÁLOGO ======================
with tab_catalog:
    st.subheader("📦 Catálogo Completo")
    tab_cat1, tab_cat2 = st.tabs(["MEUPC.NET - Componentes", "BuildRedux - Builds Prontos"])

    with tab_cat1:
        st.dataframe(catalog_df[['CATEGORY_NAME', 'PRODUCT_NAME', 'LIST_PRICE', 'DESCRIPTION']],
                     width='stretch', hide_index=True)

    with tab_cat2:
        buildredux_df['TOTAL_PRICE_BRL'] = buildredux_df['TOTAL_PRICE'] * 5.30
        st.dataframe(buildredux_df[['BUILD_NAME', 'TOTAL_PRICE_BRL', 'FULL_SPECS']],
                     width='stretch', hide_index=True)

st.caption(" Dados do MEUPC.NET + BuildRedux")