@echo off

rem Comando para instalar as dependências usando pip
pip install -r requirements.txt

rem Comando para executar o 'manage.py' do Django
python manage.py runserver
