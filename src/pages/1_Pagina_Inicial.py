import streamlit as st
import os
from datetime import datetime
from model import MetasModel

# Fallback for Tkinter in non-desktop environments
def get_file_path():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        root.destroy()
        return file_path
    except:
        return None

st.title("🚀 Página Inicial")

model = MetasModel()

col1, col2 = st.columns(2)
with col1:
    now = datetime.now()
    data_inicio = st.date_input("Data Início", value=datetime(2026, 4, 1))
with col2:
    data_fim = st.date_input("Data Fim", value=datetime(now.year, now.month, now.day))

if 'file_path' not in st.session_state:
    st.session_state.file_path = None

col_btn1, col_btn2 = st.columns([1, 3])
with col_btn1:
    if st.button("Selecionar Arquivo"):
        path = get_file_path()
        if path:
            st.session_state.file_path = path
        else:
            st.info("Selecione o arquivo manualmente no campo abaixo (ou arraste e solte):")

uploaded_file = st.file_uploader("Ou faça o upload do arquivo .xlsx", type="xlsx")
if uploaded_file:
    temp_dir = "resultado_analise"
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)
    temp_path = os.path.join(temp_dir, "input_manual.xlsx")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.file_path = temp_path

if st.session_state.file_path:
    st.success(f"Arquivo pronto: {st.session_state.file_path}")

btn_enabled = st.session_state.file_path is not None and data_inicio <= data_fim

if st.button("Executar Análise", disabled=not btn_enabled):
    with st.spinner("Processando dados..."):
        try:
            df_result = model.process_raw_data(st.session_state.file_path, data_inicio, data_fim)
            
            output_dir = "resultado_analise"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            file_name = f"analise_{data_inicio}_a_{data_fim}.xlsx"
            full_path = os.path.abspath(os.path.join(output_dir, file_name))
            
            df_result.to_excel(full_path,
                               columns=[
                                   "ID_tarefa",
                                   "Descricao",
                                   "TOM",
                                   "ORG_manut",
                                   "Tipo_temporal",
                                   "Tempo_inicio",
                                   "Horas_trabalhadas",
                                   "Tempo_fim",
                                   "Valida serviço",
                                   "Motivo inconsistente"
                               ],index=False)
            
            st.success(f"Análise concluída!")
            st.info(f"Caminho: {full_path}")
            st.session_state.last_analysis_file = full_path
        except Exception as e:
            st.error(f"Erro: {e}")
