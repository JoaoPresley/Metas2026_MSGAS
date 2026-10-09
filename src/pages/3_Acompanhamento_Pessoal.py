import streamlit as st
import numpy as np
from models.model import MetasModel, show_dataframe

st.title("👤 Acompanhamento Pessoal")

st.markdown("""
Acompanhe os resultados e o desempenho individual de cada técnico (TOM).
""")

model = MetasModel()

col_btn, _ = st.columns([1, 4])
with col_btn:
    compilar = st.button("Compilar Dados da API")

# Lógica de atualização/extração compartilhada
if compilar:
    with st.spinner("Consultando API e processando regras de negócio..."):
        try:
            # Reutiliza o fluxo completo: lê exceções, extrai dados da API e processa as métricas
            df_result = model.process_raw_data()
            
            # Atualiza o estado da sessão
            st.session_state.compiled_df = df_result
            st.success("Dados compilados e atualizados com sucesso!")
        except Exception as e:
            st.error(f"Erro durante o carregamento da API: {e}")

# Lógica de exibição caso os dados já estejam em memória
if 'compiled_df' in st.session_state:
    df = st.session_state.compiled_df
    
    st.markdown("---")
    
    # Prepara a lista de técnicos
    toms = np.sort(df["TOM"].astype(str).unique())
    selected_tom = st.selectbox("Selecione o Técnico (TOM)", toms)
    
    if selected_tom:
        df_tom = df[df["TOM"] == selected_tom]
        figs = model.generate_pie_charts(df_tom, title_prefix=selected_tom)
        
        st.markdown(f"### Desempenho de {selected_tom}")
        c1, c2, c3 = st.columns(3)
        with c1: st.pyplot(figs[0])
        with c2: st.pyplot(figs[1])
        with c3: st.pyplot(figs[2])
        
        st.subheader(f"Registros de {selected_tom}")
        st.dataframe(show_dataframe(df_tom))
else:
    st.warning("Dados não carregados na sessão. Acesse a Página Inicial ou clique em 'Compilar Dados da API'.")
