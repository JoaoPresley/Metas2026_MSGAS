class Analyses:
    def __init__(self):
        pass

    @classmethod
    def analyse(self, df_periodo):
        from models.model import MetasModel
        # Verifica se o serviço é feito sem necessidade de viagem
        df_periodo["In Loco"] = df_periodo["Descricao"].str.contains(MetasModel.no_travel_regex, case=False, na=False)

        # Valida tarefas
        df_periodo = self.__validate_tasks(df_periodo,MetasModel.task_err)

        # Cria a coluna de motivo inconsistente
        def insert_motivo(row):
            if not row["Valida serviço"]:
                if row["Tipo_temporal"] == "Viagem":
                    return "Viagem longa"
                else:
                    return "Serviço sem viagem ou mais que 8hrs"
            return ""

        df_periodo["Motivo inconsistente"] = df_periodo.apply(insert_motivo, axis=1)

        return df_periodo

    def __validate_tasks(df_periodo, task_err):
        """

        :param df_periodo:
        :return:
        """
        # Logic for validation
        servicos = df_periodo[df_periodo["Tipo_temporal"] == "Serviço"]
        viagens = df_periodo[df_periodo["Tipo_temporal"] == "Viagem"]

        viagens_ok_mask = viagens[
                              "Horas_trabalhadas"] <= 8  # (viagens["Horas_trabalhadas"] >= 4/60) & (viagens["Horas_trabalhadas"] <= 8)
        viagens_ok_mask = viagens_ok_mask | viagens["In Loco"]

        tarefas_viagem = viagens["ID_tarefa"].unique()  # Tarefas que tem viagem
        servicos_ok = ((servicos["ID_tarefa"].isin(tarefas_viagem) | servicos["In Loco"]) &
                       (servicos["Horas_trabalhadas"] <= 8))

        # Expand validation to the whole period dataframe
        df_periodo["Valida serviço"] = False

        # Mapping results back to the main dataframe
        # For Viagens
        df_periodo.loc[df_periodo["Tipo_temporal"] == "Viagem", "Valida serviço"] = viagens_ok_mask.values
        # For Serviços
        df_periodo.loc[df_periodo["Tipo_temporal"] == "Serviço", "Valida serviço"] = servicos_ok.values
        # For Tasks in exception
        df_periodo.loc[df_periodo["ID_tarefa"].isin(task_err), "Valida serviço"] = True

        return df_periodo