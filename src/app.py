import streamlit as st

st.set_page_config(
    page_title="Sistema de Metas MSGÁS",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Sistema de Metas MSGÁS")

st.markdown("""
### Bem-vindo!
O sistema foi carregado com sucesso. 

**Para navegar entre as funcionalidades, utilize a barra lateral à esquerda.**

1. **Página Inicial**: Seleção de arquivos e processamento inicial.
2. **Análise da Meta**: Visualização de gráficos consolidados.
3. **Acompanhamento Pessoal**: Filtros por técnico (TOM).
""")

st.sidebar.success("Selecione uma página acima.")
