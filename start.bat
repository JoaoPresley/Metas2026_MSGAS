@echo off
setlocal enabledelayedexpansion
title Analise metas 2026 (browser)

:: --- CONFIGURAÇÃO ---
set VENV_PATH=.venv

:: 1. Tenta detectar o Python puro ou o comando 'py'
set PY_CMD=
where py >nul 2>nul && set PY_CMD=py
if not defined PY_CMD (
    where python >nul 2>nul && set PY_CMD=python
)

:: 2. Se não achou Python, tenta detectar o Conda
if not defined PY_CMD (
    where conda >nul 2>nul
    if not errorlevel 1 (
        echo [INFO] Anaconda detectado. Criando ambiente via Conda...
        :: No Anaconda, o comando para criar venv de python puro eh esse:
        conda run python -m venv %VENV_PATH%
        set PY_CMD=python
    ) else (
        echo [ERRO] Nem Python nem Anaconda foram encontrados no seu sistema.
        pause
        exit /b
    )
)

:: 3. Cria o ambiente virtual se não existir
if not exist "%VENV_PATH%" (
    echo [INFO] Criando ambiente virtual com !PY_CMD!...
    !PY_CMD! -m venv %VENV_PATH%
)

:: 4. Ativa o ambiente virtual (.venv local)
:: O segredo aqui: mesmo que criado pelo Conda, o venv usa o activate.bat comum
echo [INFO] Ativando ambiente...
call %VENV_PATH%\Scripts\activate.bat

:: 5. Instala dependencias e roda
echo [INFO] Verificando dependencias (isso pode demorar um pouco) ...
!PY_CMD! -m pip install -r requirements.txt -qq

:: 6. Roda o streamlit
echo [INFO] Executando streamlit run src\app.py
streamlit run src\app.py

pause
call deactive