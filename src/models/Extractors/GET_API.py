
import dotenv
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

# noinspection PyUnhashable
class API:
    def __init__(self):
        """Inicializa as variaveis de API
        atributos:
            session: sessão aberta para fazer requisições
        """
        dotenv.load_dotenv()

        self.__url_api = os.getenv("BASE_API_URL")
        self.__USERNAME = os.getenv("USERNAME")
        self.__PASSWORD = os.getenv("PASSWORD")

        # Define a sessão
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                                              "Chrome/154.0.0.0 Safari/537.36"})
    def get_dataframe(self):
        """Utiliza a API para obter os dados necessários do IFS afim de analisar a meta

        :return: dataframe
        """
        try:
            response = self.session.get(self.__url_api, allow_redirects=True)
            response.raise_for_status()
            # Verifica se está pedindo login
            if "login?rf=" in response.url:
                print("System Joaozin: Realizando login")
                #está pedindo login
                response = self.__login(session=self.session, response=response)
                return self.__make_dataframe(response)
            else:
                return self.__make_dataframe(response)

        # Se pedir login
        except requests.exceptions.HTTPError as err:
            print(f"Correu um erro inesperado na requisição: {err}")

    def __login(self, session, response):
        """Realiza o login  na sessão do IFS

        :param session: sessão aperta que estará realizando a requisições REST
        :param response: resposta da requisição que fora tentado realizar
        :return: response: resposta da requisição que fora realizada
        """
        # A resposta possui um link que é o link de login
        login_url = response.url
        try:
            # Tenta fazer o login
            payload = {"username": self.__USERNAME, "password": self.__PASSWORD}
            #Tenta logar
            response_login = session.post(login_url,
                                          data=payload,
                                          allow_redirects=True)
            response_login.raise_for_status()

            # O response me devolve um formulário html para o callback com os dados para solicitar o call back
            soup = BeautifulSoup(response_login.content, "html.parser")
            # Verifica se é realmente um formulário, do contrário algo errado aconteceu
            if "form" in soup.prettify():
                form = soup.find("form")
                callback_url = form.get("action")  # link que o forms entrega
                payload = { # Dados que o form entrega
                    input_tag.get("name"): input_tag.get("value")
                    for input_tag in form.find_all("input")
                    if input_tag.get("name")
                }
            else:
                raise Exception("Falha de rota, content do callback não era o esperado")
            # Enviado callback
            response_callback = session.post(callback_url,
                                             data=payload,
                                             allow_redirects=True)
            response_callback.raise_for_status()
            # retorna a resposta
            return response_callback

        except requests.exceptions.HTTPError as err:
            print(f"Erro na etapa de login: {err}")
    def __make_dataframe(self, response):
        """Recebe a resposta da requisição da API e trata ela
        para um dataframe com as colunas necessárias para a análise.

        :param: response: resposta da requisição à API
        :return: dataframe
        """
        # Cria um dataframe com o resultado da requisição
        colunas = [
            'ClockingSeq',
            'TaskSeq',
            'ClockingType',
            'ClockingCategory',
            'EmployeeId',
            'StartTime',
            'StopTime',
            'WorkHours',
            'Site',
            'TaskDescription',
            'OrganizationId',
            'TaskSeqRef'
        ]
        df = pd.DataFrame(response.json()["value"])[colunas]
        # obtem o WorkID apartir do TaskSeqRef
        def func_workID(x):
            return x['WorkTypeId']
        df['WorkTypeID'] = df['TaskSeqRef'].apply(func_workID)
        # Retira a coluna TaskSeqRef que era util apenas para obter o WorkTypeId
        df = df.drop(columns=['TaskSeqRef'])
        return df
