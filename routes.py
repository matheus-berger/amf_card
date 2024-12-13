# Importando bibliotecas do flask
from flask import Flask, render_template, request, redirect, url_for, session


from app import app
from forms import FormCadastro, FormLogin

# Rota da Pagina Inicial
@app.route('/')
def index():
    return render_template('index.html')


# Rota do Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    from app import Login_Usuario

    if request.method == 'POST':
        ra = request.form['ra']
        senha = request.form['senha']
        print(f"RA: {ra}, Senha: {senha}")  # Log para debug
        
        usuario = Login_Usuario(ra, senha)
        mensagem = usuario.autenticar()
        print("mensagem: ", mensagem)
        
        if mensagem == "RA não cadastrado!" or mensagem == "Senha incorreta!":
            return render_template('login.html', mensagem=mensagem)
        else:
            # Usuário autenticado com sucesso, armazena o RA na sessão
            session['usuario_logado'] = ra
            return redirect(url_for('carteira'))
    
    return render_template('login.html')


# Rota do Cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    from app import Cadastro_Usuario  # Importar a classe de cadastro do usuário

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        ra = request.form['ra']
        senha = request.form['senha']
        print(f"Nome: {nome}, Email: {email}, RA: {ra}, Senha: {senha}")  # Log para debug

        # Instanciar a classe Cadastro_Usuario
        usuario = Cadastro_Usuario(nome, email, ra, senha)

        # Tentar cadastrar o usuário
        mensagem = usuario.cadastrar_usuario()

        if mensagem is True:
            # Cadastro bem-sucedido, redireciona para o login
            return redirect(url_for('login'))
        else:
            # Mostra a mensagem de erro
            return render_template('cadastro.html', mensagem=mensagem)

    # Exibe o formulário de cadastro
    return render_template('cadastro.html')



# Rota de acesso a carteira
@app.route('/carteira')
def carteira():
    from app import Tabela_Aluno, Tabela_Carteira

    if 'usuario_logado' not in session:
        # Redireciona para o login se não estiver logado
        return redirect(url_for('login'))
    
    # Busca o RA do usuário logado na sessão
    ra_usuario = session['usuario_logado']
    
    # Busca os dados do aluno no banco de dados
    aluno = Tabela_Aluno.query.filter_by(ra=ra_usuario).first()
    carteira = Tabela_Carteira.query.filter_by(aluno=ra_usuario).first()
    
    if not aluno or not carteira:
        return "Erro: Aluno ou carteira não encontrados", 404

    # Dados a serem enviados para o template
    dados_carteira = {
        "nome": aluno.nome,
        "foto": aluno.foto,  # Certifique-se de que a foto está salva como URL ou caminho acessível
        "status": "Ativo" if carteira.status == 1 else "Inativo",
        "vencimento": carteira.data_expiracao.strftime('%d/%m/%Y'),
        "tipo": carteira.tipo_cartao,
        "codigo_qr": carteira.codigo  # O valor que será usado no QR Code
    }

    return render_template('carteira.html', dados=dados_carteira)


# Rota de LogOff
@app.route('/sair')
def sair():
    session.pop('usuario_logado', None)
    return redirect(url_for('index'))


# Rodando os routes
if __name__ == '__main__':
    app.run(debug=True)
