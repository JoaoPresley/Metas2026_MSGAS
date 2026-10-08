import pandas as pd
import matplotlib.pyplot as plt

from models.Load.Analyses import Analyses

class MetasModel:
    no_travel_regex = "|".join([
        "Caf", "sobreavi", "Patru", "Calibrar esta", "Sipat",
        "Calibrar torr", "Preparar esta", "Consolida",
        "Palestra", "EQS", "recarga de tanque", "Treinamento", "test", "oficina"
    ])

    task_err = None

    def __init__(self):
        """Define variveis globais usadas na análise
        self.month_number (Dict[mês(str)] = numero(str)): Transmforma abreviação em inglês de 3 letras em numeros de 2 digitos

        self.no_travel_regex (str): Regex de nomes que caso esteja na descrição da tarefa anula o tempo de viagem.

        self.task_err (list[n° de tarefas str)]): Carra a lista de tarefas que bugaram e foram reportadas como bug
        """
        self.month_number = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "may": "05", "jun": "06", "jul": "07", "aug": "08",
            "sep": "09", "oct": "10", "nov": "11", "dec": "12"
        }

    def fill_task_err(self, arq):
        """Função para preencher a váriavel de tarefas que bugaram

        :param arq: Caminho do arquivo que está o .csv estraido o IFS com as tarefas que bugou
        :return: Void, Preenche variavel global self.task_err
        """
        df = pd.read_csv(arq,
                         encoding='latin1',
                         sep=';',
                         usecols=[#"Nº OS",
                                  "Nº Tarefa"]
                                  #"Início Real",
                                  #"Descrição"]
                         )
        MetasModel.task_err = df["Nº Tarefa"]


    def formata_data(self, d):
        """Função que formata datas da base de dados para padrão brasileiro

        :param d: mmm d, YYYY, hh:mm:ss AM/PM
        :return: dd/mm/YYYY hh:mm:ss
        """
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
        """Processa os dados do arquivo com base no inicio e término

        :param file_path: Caminho para o arquivo que está sendo analisado
        :param start_date: YYYY/MM/DD Data que será iniciado a analise
        :param end_date: YYYY/MM/DD Data que será iniciado a analise
        :return: data_frame com os dados tratados e validados no periodo solicitado
        """
        #Process de task with erros
        self.fill_task_err(r"src/outliers/Tarefas_erro.csv")

        df = pd.read_excel(file_path,
                           sheet_name='IFS_TASK_CLOCKING',
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

        # Apartir daqui é análise dos dados
        mask = (df["Tempo_inicio"] >= pd.to_datetime(start_date)) & (df["Tempo_inicio"] <= pd.to_datetime(end_date))
        df_periodo = df[mask].copy()
        df_periodo.reset_index(drop=True, inplace=True)

        print("!!!!!!!!!!Processa os dados do arquivo!!!!!!!!")

        return Analyses.analyse(df_periodo)

    def validate_compiled_data(self, df):
        """Compila o dataframe passado e verifica se as colunas estão ok e transforma os Valida serviço em serviços válidos

        :param df: DataFrame para validar
        :return: DataFrame validado
        """
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
            "TRUE": True, "FALSE": False,
            "VERDADEIRO": True, "FALSO": False,
            "1": True, "0": False,
            "1.0": True,
            "0.0": False
        })

        # If task (N° Tarefa) is in self.task_err df["Valida serviço"] = True
        return df

    def generate_pie_charts(self, df, title_prefix=""):
        """Gera um gráfico de torta com base no dataframe válido

        :param df: dataframe válido
        :param title_prefix: Título do gráfico
        :return: figura com 3 gráficos de torta
        """
        # 1. Viagens OK vs Não OK
        viagens = df[df["Tipo_temporal"] == "Viagem"]
        v_ok = len(viagens[viagens["Valida serviço"] == True])
        v_err = len(viagens[viagens["Valida serviço"] == False])
        
        # 2. Serviços com Viagem vs Sem Viagem
        servicos = df[df["Tipo_temporal"] == "Serviço"]
        s_ok = len(servicos[servicos["Valida serviço"] == True])
        s_err = len(servicos[servicos["Valida serviço"] == False])
        
        # 3. Alcance da Meta (Geral)
        total_ok = v_ok
        total_err = v_err + s_err
        
        figs = []
        cores = ["#3b6fe4", "#d36e3d"]
        
        # Chart 1 - Viagens
        fig1, ax1 = plt.subplots()
        if (v_ok + v_err) > 0:
            ax1.pie([v_ok, v_err], labels=[f"{v_ok} OK", f"{v_err} Erro"], autopct='%1.1f%%', colors=cores, explode=[0.1, 0.1] if v_err > 0 else [0, 0])
        else:
            ax1.text(0.5, 0.5, "Sem dados", ha='center')
        ax1.set_title(f"{title_prefix} - Viagens")
        figs.append(fig1)
        
        # Chart 2 - Serviços
        fig2, ax2 = plt.subplots()
        if (s_ok + s_err) > 0:
            ax2.pie([s_ok, s_err], labels=[f"{s_ok} OK", f"{s_err} Erro"], autopct='%1.1f%%', colors=cores, explode=[0.1, 0.1] if s_err > 0 else [0, 0])
        else:
            ax2.text(0.5, 0.5, "Sem dados", ha='center')
        ax2.set_title(f"{title_prefix} - Serviços")
        figs.append(fig2)
        
        # Chart 3 - Metas
        fig3, ax3 = plt.subplots()
        if (total_ok + total_err) > 0:
            ax3.pie([total_ok, total_err], labels=[f"{total_ok} OK", f"{total_err} Erro"], autopct='%1.1f%%', colors=cores, explode=[0.1, 0.1] if total_err > 0 else [0, 0])
        else:
            ax3.text(0.5, 0.5, "Sem dados", ha='center')
        ax3.set_title(f"{title_prefix} - Alcance da Meta")
        figs.append(fig3)
        
        return figs
