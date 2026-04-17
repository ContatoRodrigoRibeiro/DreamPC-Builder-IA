import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="DreamPC Builder IA", page_icon="🖥️", layout="wide")

st.title("🖥️ DreamPC Builder IA")
st.markdown("### A IA que finalmente entende seu orçamento")


# ====================== CARREGAR DADOS ======================
@st.cache_data
def load_data():
    meupc = pd.read_csv('data/hardware_catalog.csv')
    buildredux = pd.read_csv('data/buildredux_builds.csv')
    return meupc, buildredux


catalog_df, buildredux_df = load_data()

# ====================== TABS ======================
tab_builder, tab_comparator, tab_catalog = st.tabs(["🚀 Builder IA", "🔄 Comparar Peças", "📦 Catálogo Completo"])

with tab_builder:
    st.subheader("✍️ Descreva o PC dos seus sonhos (com orçamento)")

    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    prompt = st.text_area(
        "Digite aqui",
        value=st.session_state.prompt,
        placeholder="Ex: Quero um pc para estudar de R$ 3000",
        height=130,
        label_visibility="collapsed"
    )
    st.session_state.prompt = prompt

    st.markdown("**Sugestões rápidas:**")
    cols = st.columns(5)
    examples = ["Gaming 1080p/1440p", "Gaming 4K / Streaming", "Edição de Vídeo / Render / 3D",
                "Trabalho / Multitarefa / Escritório", "Estudos / Uso Geral"]
    for i, ex in enumerate(examples):
        with cols[i]:
            if st.button(ex, width='stretch', key=f"btn_{i}"):
                st.session_state.prompt = ex + " de R$ 3000"
                st.rerun()

    if st.button("🚀 Montar PC dos Sonhos com IA", type="primary", width='stretch'):
        prompt_lower = st.session_state.prompt.lower()

        # DETECÇÃO DE ORÇAMENTO
        budget_match = re.search(r'(?:até|orçamento|de|budget|r\$)\s*(\d{1,3}(?:\.\d{3})*|\d+)', prompt_lower)
        budget = int(budget_match.group(1).replace('.', '')) if budget_match else 5000

        # TIPO DE USO
        if any(x in prompt_lower for x in ["gamer", "gaming", "jogos", "1440", "1080"]):
            use_case = "gaming"
        elif any(x in prompt_lower for x in ["4k", "streaming"]):
            use_case = "4k"
        elif any(x in prompt_lower for x in ["edição", "vídeo", "render", "3d"]):
            use_case = "editing"
        elif any(x in prompt_lower for x in ["trabalho", "escritório", "multitarefa"]):
            use_case = "work"
        else:
            use_case = "general"

        # ALOCAÇÃO + LIMITES MÁXIMOS POR CATEGORIA (para evitar peças enterprise)
        alloc = {
            "gaming": {"CPU": 0.22, "Video Card": 0.48, "Mother Board": 0.12, "Storage": 0.18},
            "4k": {"CPU": 0.20, "Video Card": 0.52, "Mother Board": 0.10, "Storage": 0.18},
            "editing": {"CPU": 0.38, "Video Card": 0.35, "Mother Board": 0.12, "Storage": 0.15},
            "work": {"CPU": 0.35, "Video Card": 0.25, "Mother Board": 0.15, "Storage": 0.25},
            "general": {"CPU": 0.30, "Video Card": 0.25, "Mother Board": 0.15, "Storage": 0.30}
        }[use_case]

        max_price = {
            "gaming": {"CPU": 2500, "Video Card": 6000, "Mother Board": 1500, "Storage": 800},
            "4k": {"CPU": 3000, "Video Card": 8000, "Mother Board": 1800, "Storage": 1000},
            "editing": {"CPU": 3500, "Video Card": 5000, "Mother Board": 1800, "Storage": 800},
            "work": {"CPU": 1800, "Video Card": 1500, "Mother Board": 1200, "Storage": 600},
            "general": {"CPU": 1200, "Video Card": 1200, "Mother Board": 1000, "Storage": 500}
        }[use_case]

        # MONTAGEM
        build = {}
        for cat in ["CPU", "Video Card", "Mother Board", "Storage"]:
            target = int(budget * alloc[cat])
            items = catalog_df[catalog_df['CATEGORY_NAME'] == cat].copy()

            if items.empty:
                build[cat] = {"name": f"Sem {cat}", "price": 0, "desc": ""}
                continue

            # ORDENADO DO MAIS BARATO PARA O MAIS CARO
            items = items.sort_values(by='LIST_PRICE')

            # FILTRA APENAS O QUE CABE NO ORÇAMENTO DA CATEGORIA E NO LIMITE MÁXIMO
            possible = items[(items['LIST_PRICE'] <= target) & (items['LIST_PRICE'] <= max_price[cat])]

            if not possible.empty:
                chosen = possible.iloc[-1]  # o mais caro que ainda cabe
            else:
                chosen = items.iloc[0]  # fallback mais barato

            build[cat] = {
                "name": chosen['PRODUCT_NAME'],
                "price": float(chosen['LIST_PRICE']),
                "desc": str(chosen.get('DESCRIPTION', ''))[:100]
            }

        # UPGRADE FINAL (só se estiver muito abaixo)
        total = sum(v["price"] for v in build.values())
        if total < budget * 0.75:
            upgrade_cat = "Video Card" if use_case in ["gaming", "4k"] else "CPU"
            items = catalog_df[catalog_df['CATEGORY_NAME'] == upgrade_cat].copy()
            items = items.sort_values(by='LIST_PRICE')
            possible = items[items['LIST_PRICE'] <= budget * 0.45]
            if not possible.empty:
                build[upgrade_cat] = {
                    "name": possible.iloc[-1]['PRODUCT_NAME'],
                    "price": float(possible.iloc[-1]['LIST_PRICE']),
                    "desc": str(possible.iloc[-1].get('DESCRIPTION', ''))[:100]
                }

        total = sum(v["price"] for v in build.values())

        # EXIBE
        cols = st.columns(4)
        for col, cat in zip(cols, ["CPU", "Video Card", "Mother Board", "Storage"]):
            with col:
                st.subheader(cat if cat != "Video Card" else "Placa de Vídeo")
                st.metric(build[cat]["name"], f"R$ {build[cat]['price']:,.2f}".replace(",", "."))
                st.caption(build[cat]["desc"])

        st.markdown(f"### 💰 **Total estimado: R$ {total:,.2f}**".replace(",", "."))

        if total > budget * 1.05:
            st.warning("⚠️ Um pouco acima do orçamento")
        elif total < budget * 0.70:
            st.info("⚠️ Configuração econômica – ainda tem margem")
        else:
            st.balloons()
            st.success("✅ Perfeito dentro do seu orçamento!")

st.caption("Versão corrigida – agora a IA realmente respeita o valor do prompt")