import streamlit as st
import pandas as pd
import os
from model import MetasModel

st.title("📊 Análise da Meta")

model = MetasModel()

col_title, col_btn = st.columns([4, 1])
with col_btn:
    compilar = st.button("Compilar")

@st.cache_data
def get_compiled_data(file_path, last_modified):
    #file_path -> endereço no .xlxs
    #last_modified -> para ler o arquivo se for modificado, e não pegar do cache
    df = pd.read_excel(file_path)
    return model.validate_compiled_data(df)

output_dir = "resultado_analise"
if not os.path.exists(output_dir): os.makedirs(output_dir)
arquivos = [f for f in os.listdir(output_dir) if f.startswith("analise_") and f.endswith(".xlsx")]

if not arquivos:
    st.warning("Nenhum arquivo encontrado em 'resultado_analise/'. Processe um arquivo na Página Inicial.")
else:
    selected_file = st.selectbox("Selecione o arquivo para análise", arquivos)
    file_path = os.path.join(output_dir, selected_file)

    if compilar:
        try:
            modified_time = os.path.getmtime(file_path)

            df = get_compiled_data(file_path, modified_time)
            st.session_state.compiled_df = df
            st.success("Dados compilados!")
        except Exception as e:
            st.error(f"Erro: {e}")
            if 'compiled_df' in st.session_state: del st.session_state.compiled_df

    if 'compiled_df' in st.session_state:
        df = st.session_state.compiled_df
        figs = model.generate_pie_charts(df, title_prefix="Geral")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.pyplot(figs[0])
        with c2: st.pyplot(figs[1])
        with c3: st.pyplot(figs[2])
        
        st.subheader("Dados Consolidados")
        st.dataframe(df)
