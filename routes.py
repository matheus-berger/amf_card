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


@app.route('/carteira', defaults={'codigo_qr': None})
@app.route('/carteira/<codigo_qr>')
def carteira(codigo_qr):
    from app import Tabela_Aluno, Tabela_Carteira

    if 'usuario_logado' not in session:
        # Redireciona para o login se não estiver logado
        return redirect(url_for('login'))

    # Busca o RA do usuário logado na sessão
    ra_usuario = session['usuario_logado']

    # Busca os dados do aluno no banco de dados
    aluno = Tabela_Aluno.query.filter_by(ra=ra_usuario).first()

    # Se o código QR não foi fornecido, buscar pelo aluno logado
    carteira = Tabela_Carteira.query.filter_by(codigo=codigo_qr).first() if codigo_qr else Tabela_Carteira.query.filter_by(aluno=ra_usuario).first()

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


# Rota para o registro de uma atividade
@app.route('/atividade/<codigo_carteira>', methods=['GET', 'POST'])
def registrar_atividade(codigo_carteira):
    from app import Cadastro_Atividade

    if request.method == 'POST':
        descricao = request.form['descricao']
        
        # Usar a classe Cadastro_Atividade para registrar a atividade
        cadastro = Cadastro_Atividade(codigo_carteira, descricao)
        mensagem = cadastro.cadastrar()
        
        return render_template('registrar_atividade.html', mensagem=mensagem, codigo_carteira=codigo_carteira)

    # Renderizar a página com o formulário para a descrição
    return render_template('registrar_atividade.html', codigo_carteira=codigo_carteira)



# Rota para consultar o historico de atividades do aluno
@app.route('/historico/<codigo_carteira>', methods=['GET'])
def historico_atividades(codigo_carteira):
    from app import Tabela_Atividades
    # Consulta as atividades da carteira no banco de dados
    atividades = Tabela_Atividades.query.filter_by(codigo_carteira=codigo_carteira).order_by(Tabela_Atividades.data_atividade.desc()).all()
    return render_template('historico.html', atividades=atividades, codigo_carteira=codigo_carteira)


# Rota de LogOff
@app.route('/sair')
def sair():
    session.pop('usuario_logado', None)
    return redirect(url_for('index'))


# Rodando os routes
if __name__ == '__main__':
    app.run(debug=False)
