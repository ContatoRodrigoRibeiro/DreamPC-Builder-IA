import streamlit as st                          # Importa o Streamlit — biblioteca que cria toda a interface web do app
import pandas as pd                             # Importa o Pandas — usado para ler e manipular os arquivos CSV
import re                                       # Importa o módulo re — usado para detectar o valor do orçamento no prompt com regex

st.set_page_config(page_title="DreamPC Builder IA", page_icon="🖥️", layout="wide")
# Configura a página: título da aba, ícone e layout largo (wide)

st.title("🖥️ DreamPC Builder IA")               # Exibe o título principal no topo da aplicação
st.markdown("### A IA que entende o que você quer + Dashboard Analítico completo")
# Exibe o subtítulo usando markdown

# ====================== CARREGAR DADOS ======================
@st.cache_data                                  # Decorador que faz o Streamlit guardar o resultado da função em cache (evita recarregar os CSVs toda vez)
def load_data():                                # Define a função que carrega os dados
    meupc = pd.read_csv('data/hardware_catalog.csv')   # Lê o catálogo de componentes do MEUPC.NET
    buildredux = pd.read_csv('data/buildredux_builds.csv') # Lê os builds prontos do BuildRedux
    return meupc, buildredux                    # Retorna os dois DataFrames

catalog_df, buildredux_df = load_data()         # Executa a função e guarda os DataFrames nas variáveis

# ====================== TABS ======================
tab_builder, tab_dashboard, tab_catalog = st.tabs(["🚀 Builder IA", "📊 Dashboard Analítico", "📦 Catálogo Completo"])
# Cria as três abas principais da aplicação

# ====================== TAB 1 - BUILDER IA ======================
with tab_builder:                               # Tudo dentro deste bloco aparece na aba Builder IA
    st.subheader("✍️ Descreva o PC dos seus sonhos (com orçamento)")
    # Subtítulo da seção de prompt

    if 'prompt' not in st.session_state:        # Verifica se a variável prompt já existe na sessão
        st.session_state.prompt = ""            # Se não existe, cria ela vazia

    prompt = st.text_area(                      # Cria a caixa de texto grande para o usuário descrever o PC
        "Descreva o PC dos seus sonhos",
        value=st.session_state.prompt,
        placeholder="Ex: Quero um pc para estudar de até R$16000,00 ou um gamer bom para 1440p com 8500 reais...",
        height=130,
        label_visibility="collapsed"            # Esconde o rótulo padrão para deixar a interface mais limpa
    )

    st.session_state.prompt = prompt            # Salva o texto digitado na sessão

    st.markdown("**Sugestões rápidas:**")       # Título das sugestões rápidas
    col_sug = st.columns(5)                     # Cria 5 colunas para os botões de sugestão

    examples = [                                # Lista com os exemplos de uso
        "Gaming 1080p/1440p",
        "Gaming 4K / Streaming",
        "Edição de Vídeo / Render / 3D",
        "Trabalho / Multitarefa / Escritório",
        "Estudos / Uso Geral"
    ]

    for i, ex in enumerate(examples):           # Loop que cria um botão para cada sugestão
        with col_sug[i]:
            if st.button(ex, width='stretch', key=f"ex_{i}"):
                st.session_state.prompt = ex    # Preenche o prompt com a sugestão escolhida
                st.rerun()                      # Recarrega a página imediatamente

    if st.button("🚀 Montar PC dos Sonhos com IA", type="primary", width='stretch'):
        # Botão principal que dispara a IA
        if not st.session_state.prompt.strip(): # Se o prompt estiver vazio
            st.warning("Digite uma descrição ou escolha uma sugestão!")
            st.stop()

        st.success("🔥 IA analisando seu prompt + BuildRedux + MEUPC.NET...")

        prompt_lower = st.session_state.prompt.lower()
        # Converte o prompt para minúsculo para facilitar as buscas

        budget_match = re.search(r'(?:até|orçamento|de|até r\$|r\$)\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:[.,]\d{2})?', prompt_lower)
        # Detecta o valor do orçamento escrito no prompt
        budget = int(budget_match.group(1).replace('.', '').replace(',', '')) if budget_match else 8500
        # Converte para inteiro ou usa 8500 como padrão

        # Define a alocação de porcentagem conforme o tipo de uso
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
            # Converte preço do BuildRedux de dólar para real
            filtered = buildredux_df[buildredux_df['TOTAL_PRICE_BRL'] <= budget * 1.2].copy()
            if not filtered.empty:
                filtered['diff'] = abs(filtered['TOTAL_PRICE_BRL'] - budget)
                build_match = filtered.sort_values('diff').iloc[0]
                # Pega o build mais próximo do orçamento

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
            st.success(f"💡 **Inspirado no BuildRedux**: {build_match['BUILD_NAME']} (R$ {build_match['TOTAL_PRICE_BRL']:,.2f})")

        if total <= budget:
            st.balloons()
            st.success("✅ Configuração perfeita dentro do orçamento!")
        else:
            st.warning("⚠️ Um pouco acima do orçamento.")

# ====================== TAB 2 - DASHBOARD ANALÍTICO ======================
with tab_dashboard:
    st.subheader("📊 Dashboard Analítico de Hardware")

    col_filter1, col_filter2 = st.columns([1, 3])
    with col_filter1:
        selected_cat = st.selectbox("Filtrar por categoria", ["Todas"] + sorted(catalog_df['CATEGORY_NAME'].unique()))

    with col_filter2:
        price_range = st.slider("Faixa de preço (R$)",
                                min_value=int(catalog_df['LIST_PRICE'].min()),
                                max_value=int(catalog_df['LIST_PRICE'].max()),
                                value=(0, int(catalog_df['LIST_PRICE'].max())))

    df_view = catalog_df.copy()
    if selected_cat != "Todas":
        df_view = df_view[df_view['CATEGORY_NAME'] == selected_cat]
    df_view = df_view[(df_view['LIST_PRICE'] >= price_range[0]) & (df_view['LIST_PRICE'] <= price_range[1])]

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric("Total de Produtos", len(df_view))
    with col_kpi2:
        st.metric("Preço Médio", f"R$ {df_view['LIST_PRICE'].mean():,.2f}")
    with col_kpi3:
        st.metric("Produto Mais Caro", f"R$ {df_view['LIST_PRICE'].max():,.2f}")
    with col_kpi4:
        st.metric("Produto Mais Barato", f"R$ {df_view['LIST_PRICE'].min():,.2f}")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.bar_chart(df_view.groupby('CATEGORY_NAME')['LIST_PRICE'].mean(), width='stretch')
        st.caption("Preço médio por categoria")

    with col_chart2:
        hist = df_view['LIST_PRICE'].value_counts(bins=15, sort=False)
        hist.index = hist.index.astype(str)     # Converte o índice (intervalos) para string → elimina o warning do Altair
        st.bar_chart(hist, width='stretch')
        st.caption("Distribuição de preços")

    st.bar_chart(df_view.nlargest(15, 'LIST_PRICE').set_index('PRODUCT_NAME')['LIST_PRICE'], width='stretch')
    st.caption("Top 15 produtos mais caros")

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