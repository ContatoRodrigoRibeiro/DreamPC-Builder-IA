import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="DreamPC Builder IA", page_icon="🖥️", layout="wide")

st.title("🖥️ DreamPC Builder IA")
st.markdown("### A IA que entende o que você quer e monta o PC dos sonhos usando **MEUPC.NET** + **BuildRedux**")

# ====================== CARREGAR DADOS ======================
@st.cache_data
def load_data():
    meupc = pd.read_csv('data/hardware_catalog.csv')
    buildredux = pd.read_csv('data/buildredux_builds.csv')
    return meupc, buildredux

catalog_df, buildredux_df = load_data()

last_update = catalog_df['LAST_UPDATE'].iloc[0] if not catalog_df.empty else "N/A"
st.caption(f"📅 Última atualização MEUPC: {last_update} | "
           f"Builds BuildRedux: {len(buildredux_df)} | "
           f"Componentes MEUPC: {len(catalog_df)}")

# ====================== PROMPT PRINCIPAL ======================
st.subheader("✍️ Descreva o PC dos seus sonhos")

if 'prompt' not in st.session_state:
    st.session_state.prompt = ""

prompt = st.text_area(
    "",
    value=st.session_state.prompt,
    placeholder="Ex: Quero um PC gamer bom para 1440p com orçamento de 8000 reais...",
    height=120,
    label_visibility="collapsed"
)

# Sugestões rápidas (bonitas)
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
        if st.button(ex, use_container_width=True, key=f"ex_{i}"):
            st.session_state.prompt = ex
            st.rerun()

# ====================== SIDEBAR (só orçamento) ======================
st.sidebar.header("💰 Orçamento")
budget = st.sidebar.slider("Orçamento máximo (R$)", 3000, 40000, 8500, step=500)

# ====================== BOTÃO MONTAR ======================
if st.button("🚀 Montar PC dos Sonhos com IA", type="primary", use_container_width=True):
    if not prompt.strip():
        st.warning("Digite uma descrição ou escolha uma sugestão!")
        st.stop()

    st.success("🔥 IA analisando seu prompt + BuildRedux + MEUPC.NET...")

    # ====================== ANÁLISE DO PROMPT (inteligência da IA) ======================
    prompt_lower = prompt.lower()

    # Detecta perfil de uso
    if any(k in prompt_lower for k in ["gamer", "gaming", "jogos", "1440", "1080"]):
        purpose = "Gaming"
        allocation = {"CPU": 0.22, "Video Card": 0.48, "Mother Board": 0.10, "Storage": 0.20}
    elif any(k in prompt_lower for k in ["4k", "streaming", "stream"]):
        purpose = "Gaming 4K"
        allocation = {"CPU": 0.25, "Video Card": 0.50, "Mother Board": 0.10, "Storage": 0.15}
    elif any(k in prompt_lower for k in ["edição", "vídeo", "render", "3d", "photoshop", "premiere"]):
        purpose = "Edição / Render"
        allocation = {"CPU": 0.38, "Video Card": 0.35, "Mother Board": 0.12, "Storage": 0.15}
    elif any(k in prompt_lower for k in ["trabalho", "escritório", "multitarefa", "produtividade"]):
        purpose = "Trabalho"
        allocation = {"CPU": 0.30, "Video Card": 0.25, "Mother Board": 0.15, "Storage": 0.30}
    else:
        purpose = "Uso Geral"
        allocation = {"CPU": 0.28, "Video Card": 0.32, "Mother Board": 0.15, "Storage": 0.25}

    # Tenta extrair orçamento do prompt (ex: 8000, 5k, R$7000)
    budget_from_prompt = re.search(r'(\d{1,2}[.,]?\d{3}|\d{4,5})', prompt_lower)
    if budget_from_prompt:
        detected = int(budget_from_prompt.group(1).replace(',', '').replace('.', ''))
        if 3000 <= detected <= 40000:
            budget = detected

    # ====================== BUSCA BUILDREDUX MAIS PRÓXIMO ======================
    build_match = None
    if not buildredux_df.empty:
        filtered = buildredux_df[buildredux_df['TOTAL_PRICE'] <= budget * 1.2].copy()
        if not filtered.empty:
            filtered['diff'] = abs(filtered['TOTAL_PRICE'] - budget)
            build_match = filtered.sort_values('diff').iloc[0]

    # ====================== MONTA PC COM MEUPC ======================
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

    # ====================== EXIBE RESULTADO ======================
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
        st.success(f"💡 **Inspirado no BuildRedux**: {build_match['BUILD_NAME']} (R$ {build_match['TOTAL_PRICE']:,.2f})")

    if total <= budget:
        st.balloons()
        st.success("✅ Configuração perfeita dentro do orçamento!")
    else:
        st.warning("⚠️ Um pouco acima do orçamento.")

    st.divider()

# ====================== CATÁLOGO ======================
st.subheader("📦 Catálogo Completo")
tab1, tab2 = st.tabs(["MEUPC.NET - Componentes", "BuildRedux - Builds Prontos"])

with tab1:
    st.dataframe(catalog_df[['CATEGORY_NAME', 'PRODUCT_NAME', 'LIST_PRICE', 'DESCRIPTION']],
                 width='stretch', hide_index=True)

with tab2:
    st.dataframe(buildredux_df[['BUILD_NAME', 'TOTAL_PRICE', 'FULL_SPECS']],
                 width='stretch', hide_index=True)

st.caption("IA treinada com inteligência do BuildRedux + preços reais do MEUPC.NET")