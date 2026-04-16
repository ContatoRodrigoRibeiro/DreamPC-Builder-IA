✅ Aqui está o README.md 100% profissional, pronto para subir no GitHub!
Copie e cole o conteúdo abaixo em um arquivo chamado README.md na raiz do seu projeto.
Markdown# DreamPC Builder IA 🖥️

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)

**Monte o PC dos sonhos do seu cliente de forma inteligente e profissional.**

Uma aplicação web completa que utiliza **dados reais do MEUPC.NET** para recomendar configurações de PC perfeitas, respeitando o orçamento e o objetivo de uso do cliente (Gaming, Edição de Vídeo, Trabalho, etc.).

---

## ✨ Funcionalidades

- **Recomendação inteligente com IA** — Alocação automática de orçamento por categoria (CPU, Placa de Vídeo, Placa-Mãe e Armazenamento)
- **Dados sempre atualizados** — Scraper automático com **Playwright** que busca preços reais do MEUPC.NET
- **Interface moderna e intuitiva** — Desenvolvida com Streamlit
- **Filtros por uso** — Gaming 1080p/1440p, 4K/Streaming, Edição/Render, Trabalho ou Uso Geral
- **Catálogo completo interativo** — Fácil visualização de todos os produtos
- **Proteção contra erros** — App não quebra mesmo se alguma categoria estiver vazia



## 🚀 Como Rodar o Projeto

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/DreamPC-Builder-IA.git
cd DreamPC-Builder-IA
2. Crie e ative o ambiente virtual
Bashpython -m venv venv
venv\Scripts\Activate.ps1     # Windows PowerShell
# ou
source venv/bin/activate      # Linux / macOS
3. Instale as dependências
Bashpip install -r requirements.txt
playwright install chromium
4. Atualize o catálogo (preços do MEUPC.NET)
Bashpython scraper.py
5. Rode a aplicação
Bashstreamlit run app.py
Acesse: http://localhost:8501

📁 Estrutura do Projeto
textDreamPC-Builder-IA/
├── app.py                 # Aplicação principal (Streamlit)
├── scraper.py             # Scraper automático do MEUPC.NET
├── data/
│   └── hardware_catalog.csv   # Catálogo atualizado automaticamente
├── requirements.txt
├── README.md
└── preview.png

🛠️ Tecnologias Utilizadas

Python 3.10+
Streamlit — Interface web
Playwright — Web scraping moderno e confiável
Pandas — Manipulação de dados
BeautifulSoup + pd.read_html — Extração inteligente de tabelas


🔄 Como Atualizar o Catálogo
Basta executar:
Bashpython scraper.py
O scraper abre o navegador, navega pelas páginas do MEUPC.NET, extrai todos os produtos e salva um arquivo hardware_catalog.csv atualizado.

📌 Próximas Melhorias (Roadmap)

 Regras de compatibilidade (socket da placa-mãe × CPU)
 Exportar configuração em PDF
 Botão “Atualizar Catálogo” direto no app
 Filtro por loja/preço mínimo
 Modo dark theme
 Deploy na Streamlit Community Cloud


👨‍💻 Autor
Desenvolvido por Deeline Design
Contato: X @deelinedesign

📄 Licença
Este projeto está sob a licença MIT. Sinta-se à vontade para usar, modificar e distribuir.

⭐ Se este projeto te ajudou, não esqueça de deixar uma estrela no repositório!
