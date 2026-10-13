import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

class API:
    def __init__(self):
        """Inicializa as variaveis de API e carrega as credenciais do .env."""
        load_dotenv()

        self.__url_api = os.getenv("BASE_API_URL")
        self.__USERNAME = os.getenv("IFS_USERNAME")
        self.__PASSWORD = os.getenv("IFS_PASSWORD")

        if not all([self.__url_api, self.__USERNAME, self.__PASSWORD]):
            raise ValueError("Variáveis de ambiente (BASE_API_URL, IFS_USERNAME, IFS_PASSWORD) não foram definidas.")

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
        })

    def get_dataframe(self) -> pd.DataFrame:
        """
        Consome a API e retorna um DataFrame com as colunas esperadas.
        Filtro temporal está na URL da API.
        """
        try:
            response = self.session.get(self.__url_api, allow_redirects=True)
            response.raise_for_status()

            if "login?rf=" in response.url:
                print("API: Realizando login...")
                response = self.__login(response)
                
            return self.__make_dataframe(response)

        except requests.exceptions.RequestException as err:
            print(f"Erro inesperado na requisição: {err}")
            raise

    def __login(self, response: requests.Response) -> requests.Response:
        """Realiza o fluxo de login no IFS e retorna a resposta final."""
        login_url = response.url
        try:
            payload = {"username": self.__USERNAME, "password": self.__PASSWORD}
            response_login = self.session.post(login_url, data=payload, allow_redirects=True)
            response_login.raise_for_status()

            if "login?rf=" in response_login.url:
                raise ValueError("Falha de login: usuário ou senha incorretos.")

            soup = BeautifulSoup(response_login.content, "html.parser")
            form = soup.find("form")
            if not form:
                raise ValueError("Falha de rota: form de callback não encontrado.")

            callback_url = form.get("action")
            payload = {
                input_tag.get("name"): input_tag.get("value")
                for input_tag in form.find_all("input") if input_tag.get("name")
            }

            response_callback = self.session.post(callback_url, data=payload, allow_redirects=True)
            response_callback.raise_for_status()
            return response_callback

        except requests.exceptions.RequestException as err:
            print(f"Erro na etapa de login: {err}")
            raise

    def __make_dataframe(self, response: requests.Response) -> pd.DataFrame:
        """Transforma o JSON da API em um pd.DataFrame com as colunas requeridas."""
        try:
            data = response.json().get("value", [])
        except ValueError:
            raise ValueError("Resposta da API não é um JSON válido.")

        colunas = [
            'ClockingSeq', 'TaskSeq', 'ClockingType', 'ClockingCategory', 
            'EmployeeId', 'StartTime', 'StopTime', 'WorkHours', 
            'Site', 'TaskDescription', 'OrganizationId', 'TaskSeqRef'
        ]
        df = pd.DataFrame(data)
        
        # Garante que as colunas existam mesmo se data estiver vazio
        for col in colunas:
            if col not in df.columns:
                df[col] = None

        df = df[colunas]

        def func_workID(x):
            if isinstance(x, dict):
                return x.get('WorkTypeId')
            return None
        
        df['WorkTypeID'] = df['TaskSeqRef'].apply(func_workID)
        df = df.drop(columns=['TaskSeqRef'])
        
        return df
