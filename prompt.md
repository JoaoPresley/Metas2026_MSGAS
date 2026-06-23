Gere um prompt para estruturar esse código e apresenta-lo como um sistema
---
* Use streamlit para configurar o front-end como interção do usuário e apresentação de dados
* Use Tkinter para acessar o endereço do arquivo .xlxs na minha máquina que iremos analisar
* Esse prompt será enviado para uma IA que consegue acessar o github
---
## Crie um PR para uma branch chamada delopment

---
### 1. Instrução da pagina inicial
Quero que transforme o meu sample.ipynb em um model e utilize as páginas do
streamlit para realizar as operações de control.

Na pagina de entrada o usuário deve conseguir selecionar um periodo assim como acontece
no filtro_temporal: 
```python
filtro_temporal = df["Tempo_inicio"].between(pd.to_datetime("05/01/2026"), pd.to_datetime("05/31/2026")) #Mês de maio
```
 E deve conseguir selecionar o endereço do arquivo usando tkinter
ao invés de puxar da .env

Depois que o usuário tiver preenchido esses dois requisitos deve-se habilitar um botão: "executar analise",
após clicar nesse botão ele deve gravar o .xlsx em uma pasta .\resultado_analise\ assim 
como acontece nesse trecho do código:
```python
nome_arquivo = r".\data\Resultado_analise.xlsx"
```
o nome do arquivo será analise_{data_inicio}_a_{data_fim}, após clicar nesse botão o endereço
de onde ficou gravado o arquivo deve ser apresentado na tela.

### 2. Instrução para as páginas de análise

Na pagina inicial ele deve direcionar para uma página chamada análise da meta
Nessa página estará mostrando um botão para compilar, ao clicar nele o sitema rodará o
model que gera os gráficos e os armazena num cache. Nessa página de análise também deverá tem um espaço
mostrando o gráfico das metas gerais, como está nesse trecho do código:
```python
# 3.1 Meta
fig, ax = plt.subplots(1, 3, figsize=(10, 4))
cores = ["#3b6fe4", "#d36e3d"]

#3.1.1 Pizza de Viagens
viagens = df[df["Tipo_temporal"] == "Viagem"]
ok = len(viagens[viagens["Valida serviço"]])
erro = len(viagens[~viagens["Valida serviço"]])
fatias, text, autotext = ax[0].pie(
    [ok, erro],
    explode=[0.1, 0.1],
    autopct="%1.1f%%",
)
ax[0].legend(
    fatias,
    [f"{ok} ok", f"{erro} não ok"],
    loc="lower left",
    bbox_to_anchor=(-0.4, -0.05),
)
ax[0].set_title("Viagens apontadas ok", fontsize=15, color='white', pad=10)

#3.1.2 Pizza de Serviços
serviços = df[df["Tipo_temporal"] == "Serviço"]
ok = len(serviços[serviços["Valida serviço"]])
erro = len(serviços[~serviços["Valida serviço"]])
fatias, text, autotext = ax[1].pie(
    [ok, erro],
    explode=[0.1, 0.1],
    autopct="%1.1f%%",
)
ax[1].legend(
    fatias,
    [f"{ok} ok", f"{erro} não ok"],
    loc="lower left",
    bbox_to_anchor=(-0.4, -0.05)
)
ax[1].set_title("Serviços com viagem", fontsize=15, color='white', pad=10)
#3.1.3 Pizza da Meta
ok = len(viagens[viagens["Valida serviço"]])
total = len(viagens) + len(serviços[~serviços["Valida serviço"]])
erro = total - ok

fatias, text, autotext = ax[2].pie(
    [ok, erro],
    explode=[0.1, 0.1],
    autopct="%1.1f%%",
)
ax[2].legend(
    fatias,
    [f"{ok} ok", f"{erro} não ok"],
    loc="lower left",
    bbox_to_anchor=(-0.4, -0.05)
)
ax[2].set_title("Alcance da meta", fontsize=15, color='white', pad=10)
#3.1 Mostra grafico
plt.tight_layout()
plt.show()
```
E também uma navegação para uma pagina: acompanhamento pessoal.
Que deve mostrar os outros 3 gráficos em 3 \<div> diferentes.
Também deve mostra uma aba de selecionar que mostra os nomes dos TOMs que estão nesse array dinâmico:
```python
toms = np.array(df["TOM"].drop_duplicates(keep="first"))
```
Quando estiver selecionada ele deve mostrar os 3 grágico pizza apenas para esses TOMs, TOM é a sigla para Técnico de Operação e Manutenção.

Ambas as páginas de analise deve ter um botão no canto superior direito: compilar.
Ao clicar nele ele vai ler novamente o arquivo que está em .\resultado_analise\ e gerar os gráficos novos,
pois o usuário pode alterar o .xlsx, porém somente a coluna "Valida serviço", caso o usuário altere outra coluna ou
coloque um valor diferente de VERDADEIRO ou FALSO na coluna retorne um erro em vermelho logo abaixo do botão.

Devo conseguir navegar livremente entre as páginas seguindo o fluxo, podendo voltar para o inicio em qualquer página ou para a página anterior:
* Pagina inicial
  * Analise
    * Analise pessoal

### 3. Da execução do sistema

A root terá:
1. um start.bat
2. a pasta de "resultado_analise"
3. a pasta que rodará todo o restante do código.
Esse .bat executará o requirements.txt caso as depêndencias ainda não estiverem instaladas,
executar o streamlit e mostrar o endereço para acessar o browser.

---
Me entregue o prompt para enviar à IA
Caso precise alterar minha branch ou criar uma nova me informe
---
# Prompt do Gemini

Você é um desenvolvedor Python sênior e especialista em arquitetura de software (padrão MVC), Streamlit e automação.
Sua tarefa é ler o código estruturado no arquivo original `sample.ipynb` (que contém scripts de tratamento de dados 
da MSGÁS com Pandas) e refatorá-lo completamente para um sistema web local utilizando Streamlit.

### 🚀 REQUISITOS DE COMMIT E BRANCH (GITHUB)
1. Crie uma nova branch a partir da atual chamada `development` (se ela já não existir).
2. Todo o código gerado deve ser enviado nesta branch `development`.
3. Ao finalizar, abra um Pull Request (PR) da branch `development` para a branch principal (`main`/`master`), detalhando as alterações feitas.

---

### 📁 ESTRUTURA DE PASTAS DO PROJETO
O repositório deve ser estruturado da seguinte forma na raiz:

```

├── resultado_analise/             # Pasta onde serão salvos os arquivos gerados
├── src/                           # Código fonte do sistema
│   ├── app.py                     # Arquivo principal do Streamlit (Configuração de multipáginas)
│   ├── model.py                   # Lógica de negócio, tratamento Pandas e geração de gráficos
│   └── views/                     # Páginas do Streamlit
│       ├── 1_Pagina_Inicial.py
│       ├── 2_Analise_da_Meta.py
│       └── 3_Acompanhamento_Pessoal.py
├── requirements.txt               # Dependências do projeto (pandas, openpyxl, streamlit, matplotlib, seaborn, etc.)
└── start.bat                      # Script de inicialização automatizada

```

---

### 🛠️ ESPECIFICAÇÕES TÉCNICAS DO SISTEMA

#### 1. Arquivo de Inicialização (`start.bat`)
Deve verificar se as dependências do `requirements.txt` estão instaladas (instalar caso não estejam), iniciar a aplicação do Streamlit apontando para o `src/app.py` e exibir o endereço de acesso no navegador.

#### 2. Lógica de Negócio (`src/model.py`)
* Transforme as funções de ETL, a função `formata_data`, as validações de inconsistência de viagens ("Viagem curta ou longa" / "Serviço sem viagem") em classes/funções reutilizáveis (Model).
* Implemente uma função de re-leitura e validação para a coluna `Valida serviço`. Caso o usuário altere o arquivo Excel final, garanta que apenas valores booleanos (convertidos para String ou True/False) sejam aceitos nessa coluna. Se qualquer outra coluna for alterada ou valores inválidos forem inseridos, a função deve disparar uma exceção.

#### 3. Página Inicial (`1_Pagina_Inicial.py`)
* **Interface**: Campos para seleção de período (Data Início e Data Fim) usando o seletor de data nativo do Streamlit.
* **Seleção de Arquivo**: Um botão que acione o `Tkinter` (`tkinter.filedialog.askopenfilename`) de forma segura/isolada para que o usuário selecione o arquivo `.xlsx` original em sua máquina (substituindo o uso do `.env`).
* **Ação**: O botão "Executar Análise" só deve ser habilitado após o arquivo e o período serem selecionados.
* **Output**: Ao clicar, processar os dados via Model filtrando pelo período escolhido e gravar o arquivo em `.\resultado_analise\` com o nome padronizado: `analise_{data_inicio}_a_{data_fim}.xlsx`. Exibir o caminho completo do arquivo gravado em tela com sucesso.

#### 4. Página: Análise da Meta (`2_Analise_da_Meta.py`)
* No canto superior direito, deve haver um botão chamado **"Compilar"**. Ao ser clicado, ele lê o arquivo gerado em `.\resultado_analise\`, processa os gráficos e os armazena no cache do Streamlit (`st.cache_data`).
* Se o arquivo contiver modificações inválidas na coluna `Valida serviço` ou em qualquer outra coluna (conforme regra do Model), exibir uma mensagem de erro em vermelho (`st.error`) logo abaixo do botão.
* Apresentar em destaque os 3 gráficos de pizza gerados pelo matplotlib do código original (Viagens apontadas ok, Serviços com viagem, Alcance da meta). Os gráficos devem ser renderizados usando `st.pyplot()`.

#### 5. Página: Acompanhamento Pessoal (`3_Acompanhamento_Pessoal.py`)
* Também deve conter o botão **"Compilar"** no canto superior direito com as mesmas regras de validação e cache da página anterior.
* Deve conter um componente de seleção (`st.selectbox` ou `st.dropdown`) preenchido dinamicamente com a lista de Técnicos de Operação e Manutenção (TOMs): `toms = np.array(df["TOM"].drop_duplicates(keep="first"))`.
* Ao selecionar um TOM, a página deve renderizar os 3 gráficos de pizza correspondentes filtrados exclusivamente para aquele técnico. Cada gráfico deve ser exibido de forma organizada dentro de containers/colunas (`st.columns`) simulando as `<div>` solicitadas.

#### 6. Navegação e Fluxo
Configure a navegação multipáginas nativa do Streamlit na barra lateral para permitir que o usuário navegue livremente (voltar ao início ou avançar) entre: *Página Inicial -> Análise da Meta -> Acompanhamento Pessoal*.

Por favor, gere a estrutura de arquivos e faça o push/PR para a branch `development`.