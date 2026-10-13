import streamlit as st
from models.model import MetasModel, show_dataframe

st.set_page_config(
    page_title="Sistema de Metas MSGÁS",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Análise da Meta (Geral)")

st.markdown("""
Esta é a visão geral das metas e consolidação dos dados de manutenção. 
Para visualizar os dados por técnico, utilize a aba **Acompanhamento Pessoal** no menu lateral.
""")

model = MetasModel()

# Apenas o botão "Compilar" para iniciar a extração de dados
col_btn, _ = st.columns([1, 4])
with col_btn:
    compilar = st.button("Compilar Dados da API")

# Lógica de atualização/extração
if compilar:
    with st.spinner("Consultando API e processando regras de negócio..."):
        try:
            # Ler/processar a planilha auxiliar, atualizar a API, e rodar a análise de metas
            # Toda essa lógica está encapsulada dentro de process_raw_data()
            df_result = model.process_raw_data()
            
            # Persistir na sessão
            st.session_state.compiled_df = df_result
            st.success("Dados compilados e armazenados em memória com sucesso!")
        except Exception as e:
            st.error(f"Erro durante o carregamento da API: {e}")

# Lógica de exibição caso os dados já estejam em memória
if 'compiled_df' in st.session_state:
    df = st.session_state.compiled_df

    st.markdown("---")
    subsetores = ["CGR", "TLG"]
    selected_setor = st.selectbox("Selecione o setor", subsetores)

    # Filtrar pelo setor selecionado
    df_filtered = df[df['ORG_manut'].str.contains(selected_setor, na=False)]

    # Gerar e exibir gráficos
    figs = model.generate_pie_charts(df_filtered, title_prefix=f"Geral - {selected_setor}")
    
    c1, c2, c3 = st.columns(3)
    with c1: st.pyplot(figs[0])
    with c2: st.pyplot(figs[1])
    with c3: st.pyplot(figs[2])
    
    st.subheader("Dados Consolidados")
    st.dataframe(show_dataframe(df_filtered))
    #show_dataframe(df_filtered)
else:
    st.info("Nenhum dado em memória. Clique em 'Compilar Dados da API' para iniciar a extração.")
