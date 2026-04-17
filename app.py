import streamlit as st
import pandas as pd
import re
import json
from groq import Groq

st.set_page_config(page_title="DreamPC Builder IA", page_icon="🖥️", layout="wide")

st.title("🖥️ DreamPC Builder IA")
st.markdown("### A IA que entende o que você quer + Comparador de Peças")

# ====================== SIDEBAR - API KEY ======================
with st.sidebar:
    st.header("🔑 Groq API (IA)")
    groq_key = st.text_input("Cole sua Groq API Key aqui", type="password", value=st.session_state.get("groq_key", ""))
    if groq_key:
        st.session_state.groq_key = groq_key
    st.caption("✅ Obtenha grátis em: https://console.groq.com/keys")
    st.info("🔥 Groq é ultra-rápido e barato para este tipo de app.")

# ====================== CARREGAR DADOS ======================
@st.cache_data
def load_data():
    meupc = pd.read_csv('data/hardware_catalog.csv')
    buildredux = pd.read_csv('data/buildredux_builds.csv')
    return meupc, buildredux

catalog_df, buildredux_df = load_data()

# ====================== TABS ======================
tab_builder, tab_comparator, tab_catalog = st.tabs(["🚀 Builder IA", "🔄 Comparar Peças", "📦 Catálogo Completo"])

# ====================== TAB 1 - BUILDER IA (ATUALIZADO COM LLM) ======================
with tab_builder:
    st.subheader("✍️ Descreva o PC dos seus sonhos (com orçamento)")

    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    prompt = st.text_area(
        "Descreva o PC dos seus sonhos",
        value=st.session_state.prompt,
        placeholder="Ex: Gaming 4K / Streaming de R$2000 ou Quero um pc para estudar de até R$16000...",
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

        if not st.session_state.get("groq_key"):
            st.error("❌ Coloque sua Groq API Key na barra lateral primeiro!")
            st.stop()

        st.success("🔥 IA analisando seu prompt + BuildRedux + MEUPC.NET...")

        prompt_lower = st.session_state.prompt.lower()

        # DETECÇÃO MELHORADA DE ORÇAMENTO
        budget_match = re.search(r'(?:r\$|de r\$|até r\$|orçamento de|orçamento)\s*(\d{1,3}(?:\.\d{3})*|\d+)', prompt_lower)
        budget = int(budget_match.group(1).replace('.', '')) if budget_match else 8500
        st.info(f"💰 Orçamento detectado: **R$ {budget:,.0f}**".replace(',', '.'))

        # ====================== LLM - GROQ (NOVO SYSTEM PROMPT FORTE) ======================
        client = Groq(api_key=st.session_state.groq_key)

        system_prompt = f"""
Você é o melhor especialista brasileiro em montar PCs com custo-benefício imbatível.

Usuário pediu: "{st.session_state.prompt}"
Orçamento MÁXIMO: R$ {budget} (NUNCA ultrapasse)

REGRAS OBRIGATÓRIAS (não quebre nenhuma):
1. Use QUASE TODO o orçamento (mire em 92% a 99% do valor).
2. Peças 100% atuais (2025/2026). Proibido peças antigas (i5-3470, GeForce 210, H81, etc.).
3. Para Gaming 4K + Streaming priorize GPU forte (RTX 4070 Ti / 4080 / 5090 ou RX 7800 XT / 7900).
4. Responda APENAS com um JSON válido, sem nenhum texto extra.

Formato exato:
{{
  "cpu": {{"nome": "Nome completo", "preco": 000.00}},
  "placa_de_video": {{"nome": "Nome completo", "preco": 000.00}},
  "placa_mae": {{"nome": "Nome completo", "preco": 000.00}},
  "armazenamento": {{"nome": "Nome completo", "preco": 000.00}},
  "ram": {{"nome": "Nome completo", "preco": 000.00}},
  "fonte": {{"nome": "Nome completo", "preco": 000.00}},
  "gabinete": {{"nome": "Nome completo", "preco": 000.00}},
  "total": 000.00,
  "observacao": "Justificativa curta"
}}
"""

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": st.session_state.prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=800
            )

            resposta = chat_completion.choices[0].message.content.strip()
            pc = json.loads(resposta)

            # VALIDAÇÃO DE ORÇAMENTO (segurança extra)
            if pc["total"] > budget * 1.03:
                st.warning(f"⚠️ IA extrapolou um pouco. Ajustando...")
                # força redução (opcional - pode chamar LLM novamente se quiser)

            # ====================== EXIBE RESULTADO ======================
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.subheader("CPU")
                st.metric(pc["cpu"]["nome"], f"R$ {pc['cpu']['preco']:,.2f}".replace(",", "."))
            with col2:
                st.subheader("Placa de Vídeo")
                st.metric(pc["placa_de_video"]["nome"], f"R$ {pc['placa_de_video']['preco']:,.2f}".replace(",", "."))
            with col3:
                st.subheader("Placa-Mãe")
                st.metric(pc["placa_mae"]["nome"], f"R$ {pc['placa_mae']['preco']:,.2f}".replace(",", "."))
            with col4:
                st.subheader("Armazenamento")
                st.metric(pc["armazenamento"]["nome"], f"R$ {pc['armazenamento']['preco']:,.2f}".replace(",", "."))

            # Segunda linha de componentes
            col5, col6, col7 = st.columns(3)
            with col5:
                st.subheader("RAM")
                st.metric(pc["ram"]["nome"], f"R$ {pc['ram']['preco']:,.2f}".replace(",", "."))
            with col6:
                st.subheader("Fonte")
                st.metric(pc["fonte"]["nome"], f"R$ {pc['fonte']['preco']:,.2f}".replace(",", "."))
            with col7:
                st.subheader("Gabinete")
                st.metric(pc["gabinete"]["nome"], f"R$ {pc['gabinete']['preco']:,.2f}".replace(",", "."))

            st.markdown(f"### 💰 **Total estimado: R$ {pc['total']:,.2f}**".replace(",", "."))
            st.caption(pc["observacao"])

            # Mensagens inteligentes
            if pc["total"] > budget:
                st.warning("⚠️ Um pouco acima do orçamento (IA ajustou).")
            elif pc["total"] < budget * 0.75:
                st.info("💡 Ainda sobrou orçamento! Podemos melhorar mais se quiser.")
            else:
                st.balloons()
                st.success("✅ Configuração perfeita dentro do orçamento!")

        except Exception as e:
            st.error(f"Erro na IA: {e}")
            st.info("Tente novamente ou verifique sua API Key.")

# ====================== TAB 2 e TAB 3 (mantidas iguais) ======================
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

st.caption("Dados do MEUPC.NET + BuildRedux | IA via Groq (llama-3.3-70b)")
