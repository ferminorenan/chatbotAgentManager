#!/bin/bash

# Comando para instalar as dependências usando pip
pip install -r requirements.txt

# Comando para executar o 'manage.py' do Django
python manage.py runserver
