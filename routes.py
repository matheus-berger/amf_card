from app import app

# Importando bibliotecas do flask
from flask import Flask, render_template, redirect, url_for


@app.route('/')
def index():
    """
    Página inicial com título e botões para Login e Cadastro.
    """
    return render_template('index.html')

@app.route('/login')
def login():
    """
    Página de Login com cabeçalho e botão para voltar à página inicial.
    """
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    """
    Página de Cadastro com cabeçalho e botão para voltar à página inicial.
    """
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)
