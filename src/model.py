import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re

class MetasModel:
    def __init__(self):
        self.month_number = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "may": "05", "jun": "06", "jul": "07", "aug": "08",
            "sep": "09", "oct": "10", "nov": "11", "dec": "12"
        }
        self.no_travel_regex = "|".join([
            "Caf", "Troca de sobreavi", "Patru", "Calibrar esta", 
            "Calibrar torr", "Preparar esta", "Consolida", 
            "Palestra", "EQS", "recarga de tanque", "Treinamento", "test"
        ])

    def formata_data(self, d):
        r = str(d).strip().lower().split()
        if len(r) < 5:
            return str(d)
        day = r[1].replace(",", " ").strip()
        month = self.month_number.get(r[0], "01")
        year = r[2][:4]
        try:
            hour_part = r[3]
            is_pm = r[4] == "pm"
            hour_td = pd.to_timedelta(hour_part)
            if is_pm and hour_td < pd.to_timedelta("12:00:00"):
                hour_td += pd.to_timedelta("12:00:00")
            elif not is_pm and hour_td >= pd.to_timedelta("12:00:00"):
                hour_td -= pd.to_timedelta("12:00:00")
            
            hour_str = str(hour_td).split()[-1]
            if len(hour_str) == 7: hour_str = "0" + hour_str
            return f"{day}/{month}/{year} {hour_str}"
        except:
            return str(d)

    def process_raw_data(self, file_path, start_date, end_date):
        df = pd.read_excel(file_path, sheet_name='IFS_TASK_CLOCKING',
                           usecols=["TASK_SEQ", "TASK_DESCRIPTION", "CLOCKING_CATEGORY", 
                                   "CLOCKING_TYPE", "START_TIME", "STOP_TIME", 
                                   "WORK_HOURS", "ORGANIZATION_ID", "EMPLOYEE_ID"])
        
        df.rename(columns={
            "TASK_SEQ": "ID_tarefa",
            "TASK_DESCRIPTION": "Descricao",
            "CLOCKING_CATEGORY": "Tipo_temporal",
            "CLOCKING_TYPE": "Valida_registro",
            "START_TIME": "Tempo_inicio",
            "STOP_TIME": "Tempo_fim",
            "WORK_HOURS": "Horas_trabalhadas",
            "ORGANIZATION_ID": "ORG_manut",
            "EMPLOYEE_ID": "TOM"
        }, inplace=True)

        df.dropna(subset=["Tempo_inicio", "Tempo_fim"], inplace=True)
        df = df[df["ORG_manut"].isin(["MCGR", "OCGR", "TLG"])]

        df["Tempo_inicio"] = df["Tempo_inicio"].apply(self.formata_data)
        df["Tempo_fim"] = df["Tempo_fim"].apply(self.formata_data)
        df["Tempo_inicio"] = pd.to_datetime(df["Tempo_inicio"], format="%d/%m/%Y %H:%M:%S")
        df["Tempo_fim"] = pd.to_datetime(df["Tempo_fim"], format="%d/%m/%Y %H:%M:%S")

        mask = (df["Tempo_inicio"] >= pd.to_datetime(start_date)) & (df["Tempo_inicio"] <= pd.to_datetime(end_date))
        df_periodo = df[mask].copy()
        df_periodo.reset_index(drop=True, inplace=True)

        df_periodo["In Loco"] = df_periodo["Descricao"].str.contains(self.no_travel_regex, case=False, na=False)

        # Logic for validation
        servicos = df_periodo[df_periodo["Tipo_temporal"] == "Serviço"]
        viagens = df_periodo[df_periodo["Tipo_temporal"] == "Viagem"]

        viagens_ok_mask = (viagens["Horas_trabalhadas"] >= 4/60) & (viagens["Horas_trabalhadas"] <= 8)
        viagens_ok_mask = viagens_ok_mask | viagens["In Loco"]
        
        tarefas_viagem = viagens["ID_tarefa"].unique()
        servicos_com_viagem = servicos["ID_tarefa"].isin(tarefas_viagem) | servicos["In Loco"]

        # Expand validation to the whole period dataframe
        df_periodo["Valida serviço"] = False
        
        # Mapping results back to the main dataframe
        # For Viagens
        df_periodo.loc[df_periodo["Tipo_temporal"] == "Viagem", "Valida serviço"] = viagens_ok_mask.values
        # For Serviços
        df_periodo.loc[df_periodo["Tipo_temporal"] == "Serviço", "Valida serviço"] = servicos_com_viagem.values

        def insert_motivo(row):
            if not row["Valida serviço"]:
                if row["Tipo_temporal"] == "Viagem":
                    return "Viagem curta ou longa"
                else:
                    return "Serviço sem viagem"
            return ""

        df_periodo["Motivo inconsistente"] = df_periodo.apply(insert_motivo, axis=1)
        
        return df_periodo

    def validate_compiled_data(self, df):
        # Rule: Valida serviço must be boolean-like (True/False/1/0)
        # Any other change in other columns or invalid values should raise exception
        required_cols = ["ID_tarefa", "Tempo_inicio", "Horas_trabalhadas", "Tempo_fim", 
                         "Tipo_temporal", "TOM", "ORG_manut", "Descricao", 
                         "Valida serviço", "Motivo inconsistente"]
        
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Coluna obrigatória ausente: {col}")
        
        # Validate 'Valida serviço' column
        # Convert to string to handle various types of boolean inputs
        df["Valida serviço"] = df["Valida serviço"].astype(str).str.upper()
        valid_values = ["TRUE", "FALSE", "1", "0", "1.0", "0.0"]
        if not df["Valida serviço"].isin(valid_values).all():
            raise ValueError("A coluna 'Valida serviço' contém valores inválidos.")
            
        # Convert to boolean for internal use
        df["Valida serviço"] = df["Valida serviço"].map({
            "TRUE": True, "FALSE": False, "1": True, "0": False, "1.0": True, "0.0": False
        })
        return df

    def generate_pie_charts(self, df, title_prefix=""):
        # 1. Viagens OK vs Não OK
        viagens = df[df["Tipo_temporal"] == "Viagem"]
        v_ok = len(viagens[viagens["Valida serviço"] == True])
        v_err = len(viagens[viagens["Valida serviço"] == False])
        
        # 2. Serviços com Viagem vs Sem Viagem
        servicos = df[df["Tipo_temporal"] == "Serviço"]
        s_ok = len(servicos[servicos["Valida serviço"] == True])
        s_err = len(servicos[servicos["Valida serviço"] == False])
        
        # 3. Alcance da Meta (Geral)
        total_ok = v_ok + s_ok
        total_err = v_err + s_err
        
        figs = []
        cores = ["#3b6fe4", "#d36e3d"]
        
        # Chart 1
        fig1, ax1 = plt.subplots()
        if (v_ok + v_err) > 0:
            ax1.pie([v_ok, v_err], labels=[f"{v_ok} OK", f"{v_err} Erro"], autopct='%1.1f%%', colors=cores, explode=[0.1, 0.1] if v_err > 0 else [0, 0])
        else:
            ax1.text(0.5, 0.5, "Sem dados", ha='center')
        ax1.set_title(f"{title_prefix} - Viagens")
        figs.append(fig1)
        
        # Chart 2
        fig2, ax2 = plt.subplots()
        if (s_ok + s_err) > 0:
            ax2.pie([s_ok, s_err], labels=[f"{s_ok} OK", f"{s_err} Erro"], autopct='%1.1f%%', colors=cores, explode=[0.1, 0.1] if s_err > 0 else [0, 0])
        else:
            ax2.text(0.5, 0.5, "Sem dados", ha='center')
        ax2.set_title(f"{title_prefix} - Serviços")
        figs.append(fig2)
        
        # Chart 3
        fig3, ax3 = plt.subplots()
        if (total_ok + total_err) > 0:
            ax3.pie([total_ok, total_err], labels=[f"{total_ok} OK", f"{total_err} Erro"], autopct='%1.1f%%', colors=cores, explode=[0.1, 0.1] if total_err > 0 else [0, 0])
        else:
            ax3.text(0.5, 0.5, "Sem dados", ha='center')
        ax3.set_title(f"{title_prefix} - Alcance da Meta")
        figs.append(fig3)
        
        return figs
