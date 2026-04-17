import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="DreamPC Builder IA", page_icon="🖥️", layout="wide")

st.title("🖥️ DreamPC Builder IA")
st.markdown("### A IA que realmente entende seu orçamento")


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
        placeholder="Ex: Quero um pc gamer bom para 1440p de R$ 4500",
        height=130,
        label_visibility="collapsed"
    )
    st.session_state.prompt = prompt

    st.markdown("**Sugestões rápidas:**")
    col_sug = st.columns(5)
    examples = ["Gaming 1080p/1440p", "Gaming 4K / Streaming", "Edição de Vídeo / Render / 3D",
                "Trabalho / Multitarefa / Escritório", "Estudos / Uso Geral"]

    for i, ex in enumerate(examples):
        with col_sug[i]:
            if st.button(ex, width='stretch', key=f"ex_{i}"):
                st.session_state.prompt = ex
                st.rerun()

    if st.button("🚀 Montar PC dos Sonhos com IA", type="primary", width='stretch'):
        if not st.session_state.prompt.strip():
            st.warning("Digite algo ou escolha uma sugestão!")
            st.stop()

        st.success("🔥 IA analisando seu prompt + BuildRedux + MEUPC.NET...")

        prompt_lower = st.session_state.prompt.lower()

        # ==================== DETECÇÃO DE ORÇAMENTO ====================
        budget_match = re.search(r'(?:até|orçamento|de|até r\$|r\$|budget)\s*(\d{1,3}(?:\.\d{3})*|\d+)', prompt_lower)
        budget = int(budget_match.group(1).replace('.', '')) if budget_match else 5000

        # ==================== TIPO DE USO ====================
        if any(k in prompt_lower for k in ["gamer", "gaming", "jogos", "1440", "1080"]):
            use_case = "gaming"
        elif any(k in prompt_lower for k in ["4k", "streaming"]):
            use_case = "4k"
        elif any(k in prompt_lower for k in ["edição", "vídeo", "render", "3d"]):
            use_case = "editing"
        elif any(k in prompt_lower for k in ["trabalho", "escritório", "multitarefa"]):
            use_case = "work"
        else:
            use_case = "general"

        # Alocações realistas (soma = 100%)
        alloc = {
            "gaming": {"CPU": 0.22, "Video Card": 0.48, "Mother Board": 0.12, "Storage": 0.18},
            "4k": {"CPU": 0.20, "Video Card": 0.52, "Mother Board": 0.11, "Storage": 0.17},
            "editing": {"CPU": 0.38, "Video Card": 0.35, "Mother Board": 0.12, "Storage": 0.15},
            "work": {"CPU": 0.35, "Video Card": 0.25, "Mother Board": 0.15, "Storage": 0.25},
            "general": {"CPU": 0.30, "Video Card": 0.30, "Mother Board": 0.15, "Storage": 0.25}
        }[use_case]

        # ==================== MONTAGEM COM RESPEITO AO ORÇAMENTO ====================
        build = {}
        for cat in ["CPU", "Video Card", "Mother Board", "Storage"]:
            target = int(budget * alloc[cat])
            items = catalog_df[catalog_df['CATEGORY_NAME'] == cat].copy()

            if items.empty:
                build[cat] = {"name": f"Sem {cat}", "price": 0, "desc": ""}
                continue

            items = items.sort_values(by='LIST_PRICE', ascending=False)  # ← Mais caro primeiro
            chosen = items[items['LIST_PRICE'] <= target].iloc[0] if not items[items['LIST_PRICE'] <= target].empty else \
            items.iloc[0]

            build[cat] = {
                "name": chosen['PRODUCT_NAME'],
                "price": float(chosen['LIST_PRICE']),
                "desc": str(chosen.get('DESCRIPTION', ''))[:90]
            }

        # ==================== LOOP DE UPGRADE AUTOMÁTICO ====================
        total = sum(item["price"] for item in build.values())
        attempts = 0
        while total < budget * 0.88 and attempts < 8:  # Tenta chegar perto dos 88% do orçamento
            attempts += 1
            # Qual componente mais importante para upar?
            if use_case in ["gaming", "4k"]:
                upgrade_cat = "Video Card"
            else:
                upgrade_cat = "CPU"

            items = catalog_df[catalog_df['CATEGORY_NAME'] == upgrade_cat].copy()
            if items.empty:
                break
            items = items.sort_values(by='LIST_PRICE', ascending=False)

            # Pega o próximo item mais caro que ainda caiba
            current_price = build[upgrade_cat]["price"]
            better = items[items['LIST_PRICE'] > current_price].iloc[:5]  # top 5 mais caros

            if not better.empty:
                new_item = better.iloc[0]
                if total - current_price + new_item['LIST_PRICE'] <= budget * 1.05:
                    build[upgrade_cat] = {
                        "name": new_item['PRODUCT_NAME'],
                        "price": float(new_item['LIST_PRICE']),
                        "desc": str(new_item.get('DESCRIPTION', ''))[:90]
                    }
                    total = sum(item["price"] for item in build.values())
            else:
                break

        # ====================== EXIBE O RESULTADO ======================
        col1, col2, col3, col4 = st.columns(4)
        for col, cat in zip([col1, col2, col3, col4], ["CPU", "Video Card", "Mother Board", "Storage"]):
            with col:
                st.subheader(cat if cat != "Video Card" else "Placa de Vídeo")
                st.metric(build[cat]["name"], f"R$ {build[cat]['price']:,.2f}".replace(",", "."))
                st.caption(build[cat]["desc"])

        st.markdown(f"### 💰 **Total estimado: R$ {total:,.2f}**".replace(",", "."))

        # Mensagem clara
        if total > budget * 1.05:
            st.warning("⚠️ Um pouco acima do orçamento.")
        elif total < budget * 0.70:
            st.info("⚠️ Configuração econômica. Ainda tem bastante margem para upgrades.")
        else:
            st.balloons()
            st.success("✅ Configuração excelente dentro do seu orçamento!")

st.caption("Dados do MEUPC.NET + BuildRedux | Versão corrigida 2026")