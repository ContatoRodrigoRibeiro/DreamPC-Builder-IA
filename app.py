import streamlit as st                          # Importa a biblioteca Streamlit — responsável por criar toda a interface web do aplicativo
import pandas as pd                             # Importa o Pandas — usado para ler e manipular os arquivos CSV (catálogo de hardware e builds do BuildRedux)
import re                                       # Importa o módulo re — usado para fazer buscas com expressões regulares (ex: detectar o valor do orçamento no prompt)

st.set_page_config(page_title="DreamPC Builder IA", page_icon="🖥️", layout="wide")
# Define as configurações iniciais da página: título da aba, ícone e layout largo (wide)

st.title("🖥️ DreamPC Builder IA")               # Exibe o título principal da aplicação na parte superior
st.markdown("### A IA que entende o que você quer + Dashboard Analítico completo")
# Exibe um subtítulo explicativo usando markdown

# ====================== CARREGAR DADOS ======================
@st.cache_data                                  # Decorador que faz o Streamlit guardar em cache o resultado da função (evita recarregar os CSVs toda vez)
def load_data():                                # Define uma função chamada load_data que será executada apenas uma vez
    meupc = pd.read_csv('data/hardware_catalog.csv')   # Lê o arquivo CSV com todos os componentes do site MEUPC.NET
    buildredux = pd.read_csv('data/buildredux_builds.csv') # Lê o arquivo CSV com os builds prontos do BuildRedux
    return meupc, buildredux                    # Retorna os dois DataFrames para serem usados no resto do app

catalog_df, buildredux_df = load_data()         # Chama a função e armazena os dois DataFrames nas variáveis catalog_df e buildredux_df

# ====================== TABS ======================
tab_builder, tab_dashboard, tab_catalog = st.tabs(["🚀 Builder IA", "📊 Dashboard Analítico", "📦 Catálogo Completo"])
# Cria as três abas principais da aplicação

# ====================== TAB 1 - BUILDER IA ======================
with tab_builder:                               # Tudo que estiver dentro deste bloco aparece na aba "Builder IA"
    st.subheader("✍️ Descreva o PC dos seus sonhos (com orçamento)")
    # Exibe um subtítulo na aba do Builder

    if 'prompt' not in st.session_state:        # Verifica se a variável 'prompt' já existe na sessão do usuário
        st.session_state.prompt = ""            # Se não existir, cria ela vazia (evita erro na primeira execução)

    prompt = st.text_area(                      # Cria uma caixa de texto grande (text_area) para o usuário descrever o PC
        "Descreva o PC dos seus sonhos",
        value=st.session_state.prompt,          # Usa o valor que já estava salvo na sessão
        placeholder="Ex: Quero um pc para estudar de até R$16000,00 ou um gamer bom para 1440p com 8500 reais...",
        height=130,
        label_visibility="collapsed"            # Esconde o rótulo padrão do Streamlit (deixa a interface mais limpa)
    )

    st.session_state.prompt = prompt            # Salva o que o usuário digitou na sessão para manter o texto ao recarregar

    st.markdown("**Sugestões rápidas:**")       # Título das sugestões rápidas
    col_sug = st.columns(5)                     # Cria 5 colunas lado a lado para os botões de sugestão

    examples = [                                # Lista com os 5 exemplos de uso
        "Gaming 1080p/1440p",
        "Gaming 4K / Streaming",
        "Edição de Vídeo / Render / 3D",
        "Trabalho / Multitarefa / Escritório",
        "Estudos / Uso Geral"
    ]

    for i, ex in enumerate(examples):           # Loop que cria um botão para cada sugestão
        with col_sug[i]:                        # Coloca o botão na coluna correspondente
            if st.button(ex, use_container_width=True, key=f"ex_{i}"):
                st.session_state.prompt = ex    # Quando o botão é clicado, preenche o prompt com a sugestão
                st.rerun()                      # Força o Streamlit a recarregar a página imediatamente

    if st.button("🚀 Montar PC dos Sonhos com IA", type="primary", use_container_width=True):
        # Botão principal que dispara toda a lógica da IA
        if not st.session_state.prompt.strip(): # Se o prompt estiver vazio, mostra aviso
            st.warning("Digite uma descrição ou escolha uma sugestão!")
            st.stop()                           # Para a execução do código

        st.success("🔥 IA analisando seu prompt + BuildRedux + MEUPC.NET...")
        # Mensagem de carregamento

        prompt_lower = st.session_state.prompt.lower()
        # Converte o prompt para minúsculo para facilitar as buscas

        budget_match = re.search(r'(?:até|orçamento|de|até r\$|r\$)\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:[.,]\d{2})?', prompt_lower)
        # Usa regex para encontrar o valor do orçamento escrito no prompt
        budget = int(budget_match.group(1).replace('.', '').replace(',', '')) if budget_match else 8500
        # Converte o número encontrado para inteiro ou usa 8500 como padrão

        # Define a distribuição de porcentagem do orçamento conforme o tipo de uso
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

        build_match = None                      # Variável que vai guardar o build do BuildRedux mais próximo
        if not buildredux_df.empty:             # Se o DataFrame do BuildRedux não estiver vazio
            buildredux_df['TOTAL_PRICE_BRL'] = buildredux_df['TOTAL_PRICE'] * 5.30
            # Converte preço de dólar para real (multiplica por 5.30)
            filtered = buildredux_df[buildredux_df['TOTAL_PRICE_BRL'] <= budget * 1.2].copy()
            # Filtra apenas os builds que não ultrapassam 120% do orçamento
            if not filtered.empty:
                filtered['diff'] = abs(filtered['TOTAL_PRICE_BRL'] - budget)
                # Calcula a diferença entre o preço do build e o orçamento do usuário
                build_match = filtered.sort_values('diff').iloc[0]
                # Pega o build mais próximo do orçamento

        build = {}                              # Dicionário que vai guardar os componentes escolhidos
        remaining = budget                      # Variável auxiliar para controlar o dinheiro restante

        for cat in ["CPU", "Video Card", "Mother Board", "Storage"]:
            # Loop que monta um componente por vez
            cat_budget = int(remaining * allocation[cat])
            # Calcula quanto dinheiro pode gastar nessa categoria
            items = catalog_df[catalog_df['CATEGORY_NAME'] == cat].copy()
            # Filtra os produtos da categoria atual

            if items.empty:                     # Se não encontrou nenhum produto
                build[cat] = {"name": f"Sem {cat} disponível", "price": 0, "desc": ""}
                continue

            items = items.sort_values(by='LIST_PRICE')
            # Ordena do mais barato para o mais caro
            best = items[items['LIST_PRICE'] <= cat_budget]
            # Filtra apenas os que cabem no orçamento da categoria
            chosen = best.iloc[-1] if not best.empty else items.iloc[0]
            # Pega o mais caro possível dentro do limite (ou o mais barato se nenhum couber)

            build[cat] = {                      # Salva as informações do componente escolhido
                "name": chosen['PRODUCT_NAME'],
                "price": chosen['LIST_PRICE'],
                "desc": chosen.get('DESCRIPTION', '')[:100]
            }
            remaining -= chosen['LIST_PRICE']   # Desconta o preço do dinheiro restante

        col1, col2, col3, col4 = st.columns(4)  # Cria 4 colunas para exibir os componentes lado a lado

        with col1:                              # Bloco da CPU
            st.subheader("CPU")
            st.metric(build["CPU"]["name"], f"R$ {build['CPU']['price']:,.2f}".replace(",", "."))
            st.caption(build["CPU"]["desc"])

        with col2:                              # Bloco da Placa de Vídeo
            st.subheader("Placa de Vídeo")
            st.metric(build["Video Card"]["name"], f"R$ {build['Video Card']['price']:,.2f}".replace(",", "."))
            st.caption(build["Video Card"]["desc"])

        with col3:                              # Bloco da Placa-Mãe
            st.subheader("Placa-Mãe")
            st.metric(build["Mother Board"]["name"], f"R$ {build['Mother Board']['price']:,.2f}".replace(",", "."))
            st.caption(build["Mother Board"]["desc"])

        with col4:                              # Bloco do Armazenamento
            st.subheader("Armazenamento")
            st.metric(build["Storage"]["name"], f"R$ {build['Storage']['price']:,.2f}".replace(",", "."))
            st.caption(build["Storage"]["desc"])

        total = sum(item["price"] for item in build.values())
        # Calcula o preço total da configuração montada

        st.markdown(f"### 💰 **Total estimado: R$ {total:,.2f}**".replace(",", "."))
        # Mostra o total com formatação brasileira

        if build_match is not None:             # Se encontrou um build do BuildRedux próximo
            st.success(f"💡 **Inspirado no BuildRedux**: {build_match['BUILD_NAME']} (R$ {build_match['TOTAL_PRICE_BRL']:,.2f})")

        if total <= budget:                     # Se ficou dentro do orçamento
            st.balloons()                       # Solta balões de festa
            st.success("✅ Configuração perfeita dentro do orçamento!")
        else:
            st.warning("⚠️ Um pouco acima do orçamento.")

# ====================== TAB 2 - DASHBOARD ANALÍTICO ======================
with tab_dashboard:                             # Tudo dentro deste bloco aparece na aba Dashboard
    st.subheader("📊 Dashboard Analítico de Hardware")
    # Título do dashboard

    col_filter1, col_filter2 = st.columns([1, 3])
    # Cria duas colunas para os filtros

    with col_filter1:
        selected_cat = st.selectbox("Filtrar por categoria", ["Todas"] + sorted(catalog_df['CATEGORY_NAME'].unique()))
        # Caixa de seleção para filtrar por categoria

    with col_filter2:
        price_range = st.slider("Faixa de preço (R$)",
                                min_value=int(catalog_df['LIST_PRICE'].min()),
                                max_value=int(catalog_df['LIST_PRICE'].max()),
                                value=(0, int(catalog_df['LIST_PRICE'].max())))
        # Slider para filtrar por faixa de preço

    df_view = catalog_df.copy()                 # Faz uma cópia do catálogo para não alterar o original
    if selected_cat != "Todas":                 # Se o usuário escolheu uma categoria específica
        df_view = df_view[df_view['CATEGORY_NAME'] == selected_cat]
    df_view = df_view[(df_view['LIST_PRICE'] >= price_range[0]) & (df_view['LIST_PRICE'] <= price_range[1])]
    # Aplica o filtro de preço

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    # Cria 4 colunas para os KPIs (indicadores principais)

    with col_kpi1:
        st.metric("Total de Produtos", len(df_view))
    with col_kpi2:
        st.metric("Preço Médio", f"R$ {df_view['LIST_PRICE'].mean():,.2f}")
    with col_kpi3:
        st.metric("Produto Mais Caro", f"R$ {df_view['LIST_PRICE'].max():,.2f}")
    with col_kpi4:
        st.metric("Produto Mais Barato", f"R$ {df_view['LIST_PRICE'].min():,.2f}")

    col_chart1, col_chart2 = st.columns(2)      # Duas colunas para os gráficos

    with col_chart1:
        st.bar_chart(df_view.groupby('CATEGORY_NAME')['LIST_PRICE'].mean(), use_container_width=True)
        # Gráfico de barras: preço médio por categoria
        st.caption("Preço médio por categoria")

    with col_chart2:
        hist = df_view['LIST_PRICE'].value_counts(bins=15, sort=False)
        # Cria histograma de distribuição de preços
        st.bar_chart(hist, use_container_width=True)
        st.caption("Distribuição de preços")

    st.bar_chart(df_view.nlargest(15, 'LIST_PRICE').set_index('PRODUCT_NAME')['LIST_PRICE'],
                 use_container_width=True)
    # Gráfico de barras com os 15 produtos mais caros
    st.caption("Top 15 produtos mais caros")

# ====================== TAB 3 - CATÁLOGO ======================
with tab_catalog:                               # Tudo dentro deste bloco aparece na aba Catálogo
    st.subheader("📦 Catálogo Completo")        # Título da aba

    tab_cat1, tab_cat2 = st.tabs(["MEUPC.NET - Componentes", "BuildRedux - Builds Prontos"])
    # Cria duas sub-abas dentro do catálogo

    with tab_cat1:                              # Primeira sub-aba: componentes do MEUPC.NET
        st.dataframe(catalog_df[['CATEGORY_NAME', 'PRODUCT_NAME', 'LIST_PRICE', 'DESCRIPTION']],
                     use_container_width=True, hide_index=True)
        # Mostra a tabela completa de componentes

    with tab_cat2:                              # Segunda sub-aba: builds do BuildRedux
        buildredux_df['TOTAL_PRICE_BRL'] = buildredux_df['TOTAL_PRICE'] * 5.30
        # Converte os preços para Real
        st.dataframe(buildredux_df[['BUILD_NAME', 'TOTAL_PRICE_BRL', 'FULL_SPECS']],
                     use_container_width=True, hide_index=True)
        # Mostra a tabela de builds prontos
