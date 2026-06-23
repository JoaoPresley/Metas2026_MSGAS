@echo off
set VENV_DIR=venv

if not exist %VENV_DIR% (
    echo Criando ambiente virtual...
    python -m venv %VENV_DIR%
)

echo Ativando ambiente virtual...
call %VENV_DIR%\Scripts\activate

echo Verificando dependencias...
pip install -r requirements.txt

echo Iniciando Sistema de Metas MSGAS...
streamlit run src/app.py
pause
