import streamlit as st
import pandas as pd
import os
import numpy as np
from model import MetasModel

st.title("👤 Acompanhamento Pessoal")

model = MetasModel()

col_title, col_btn = st.columns([4, 1])
with col_btn:
    compilar = st.button("Compilar")

@st.cache_data
def get_compiled_data(file_path):
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
            df = get_compiled_data(file_path)
            st.session_state.compiled_df = df
            st.success("Dados compilados!")
        except Exception as e:
            st.error(f"Erro: {e}")
            if 'compiled_df' in st.session_state: del st.session_state.compiled_df

    if 'compiled_df' in st.session_state:
        df = st.session_state.compiled_df
        
        toms = np.sort(df["TOM"].unique())
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
            st.dataframe(df_tom)
