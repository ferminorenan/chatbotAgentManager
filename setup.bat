@echo off

rem Verifica se o argumento '--debug' foi passado
if "%1"=="--debug" (
    echo DEBUG="true" > .env
    echo ALLOWED_HOSTS="*" >> .env
    if not exist ".env" (
        ECHO Digite a SECRET_KEY desejada: 
        SET /P secret_key=
        goto set_env
        :set_env
        ECHO SECRET_KEY="%secret_key%" >> .env
    )
)
rem Comando para instalar as dependências usando pip
pip install -r requirements.txt
rem Comando para executar o 'manage.py' do Django
python manage.py install