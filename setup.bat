@echo off

rem Comando para instalar as dependências usando pip
pip install -r requirements.txt

rem Função para verificar se uma variável de ambiente está definida
:check_env_var
setlocal
set VAR_VALUE=%~2
if "%VAR_VALUE%"=="" (
    endlocal
    exit /b 1
) else (
    endlocal
    exit /b 0
)

rem Verifica se o argumento --debug foi passado
set DEBUG_MODE=false
if "%~1"=="--debug" (
    set DEBUG_MODE=true
)

rem Verifica se as variáveis de ambiente necessárias estão definidas

call :check_env_var DEBUG %DEBUG%
if %errorlevel% neq 0 (
    if "%DEBUG_MODE%"=="true" (
        set DEBUG=true
    ) else (
        set DEBUG=false
    )
    echo DEBUG=%DEBUG%>>.env
)

call :check_env_var ALLOWED_HOSTS %ALLOWED_HOSTS%
if %errorlevel% neq 0 (
    if "%DEBUG_MODE%"=="true" (
        set ALLOWED_HOSTS=*
    ) else (
        set /p ALLOWED_HOSTS=Por favor, insira o valor para ALLOWED_HOSTS: 
    )
    echo ALLOWED_HOSTS=%ALLOWED_HOSTS%>>.env
)

rem Comando para executar o 'manage.py' do Django
python manage.py install
