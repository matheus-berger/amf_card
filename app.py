# Importando as bibliotecas necessarias
import random
import string
import uuid
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Criando a aplicação
app = Flask(__name__)

# Importando o conteudo de routes
import routes

# Criando a estrutura do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amf_card.db'
db = SQLAlchemy(app)


# Classe responsável por criar a tabela Aluno
class Tabela_Aluno(db.Model):
    __tablename__ = 'aluno'
    ra = db.Column(db.String(6), primary_key=True)
    foto = db.Column(db.String(255), default='static/img/usuario_padrao.png')
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)


# Classe responsável por criar a tabela Carteira
class Tabela_Carteira(db.Model):
    __tablename__ = 'carteira'
    codigo = db.Column(db.String(15), unique=True, primary_key=True)
    aluno = db.Column(db.String(6), db.ForeignKey('aluno.ra'), nullable=False)
    tipo_cartao = db.Column(db.String(20), default='Standard')
    status = db.Column(db.Boolean, default=True)
    data_emissao = db.Column(db.Date, default=lambda: datetime.now())
    data_expiracao = db.Column(db.Date, default=lambda: datetime.now() + timedelta(days=4*365))

    dono_carteira = db.relationship('Tabela_Aluno', backref='carteira')


# Classe responsavel pelo cadastro do usuario no banco de dados
class Cadastro_Usuario:
    def __init__(self, nome, email, ra, senha):
        self.nome = nome
        self.email = email
        self.ra = ra
        self.senha = senha

    # Método para verificar se o RA já existe no banco
    def validar_ra(self):
        aluno_existente = Tabela_Aluno.query.filter_by(ra=self.ra).first()
        if aluno_existente:
            return f"O RA {self.ra} já está cadastrado."
        return None

    def cadastrar_usuario(self):
        # Validar RA
        mensagem = self.validar_ra()
        if mensagem:
            return mensagem
        
        # Gerar o hash da senha
        senha_hash = generate_password_hash(self.senha)

        # Cadastrar o aluno no banco de dados o aluno
        novo_aluno = Tabela_Aluno(
            ra=self.ra,
            nome=self.nome,
            email=self.email,
            senha_hash = senha_hash
        )
        db.session.add(novo_aluno)
        db.session.commit()

        # Cadastrar a carteira
        cadastro_carteira = Cadastro_Carteira(self.ra)
        if cadastro_carteira.cadastrar() is True:
            return f"Usuário {self.nome} cadastrado com sucesso!"
        else:
            return "Erro ao cadastrar a carteira do usuário."


# Classe responsavel pelo cadastro da Carteira
class Cadastro_Carteira:
    def __init__(self, ra):
        self.ra = ra

    def validar_aluno(self):
        # Verifica se o aluno existe no banco de dados
        aluno = Tabela_Aluno.query.filter_by(ra=self.ra).first()
        if not aluno:
            return f"Aluno com RA {self.ra} não encontrado."
        return aluno

    def verificar_carteira_existente(self):
        # Verifica se o aluno já possui uma carteira
        carteira_existente = Tabela_Carteira.query.filter_by(aluno=self.ra).first()
        if carteira_existente:
            return f"Carteira já cadastrada para o RA {self.ra}."
        return None

    def gerar_codigo_unico(self):
        # Gera um código único para a carteira
        while True:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
            # Verifica se o código já existe no banco
            if not Tabela_Carteira.query.filter_by(codigo=codigo).first():
                return codigo

    def cadastrar(self):
        # Valida o aluno
        aluno = self.validar_aluno()
        if isinstance(aluno, str):
            return aluno  # Retorna mensagem de erro

        # Verifica se já existe uma carteira cadastrada
        mensagem = self.verificar_carteira_existente()
        if mensagem:
            return mensagem  # Retorna mensagem de erro

        # Gera o código da carteira
        codigo_carteira = self.gerar_codigo_unico()

        # Cria e salva a carteira no banco
        nova_carteira = Tabela_Carteira(
            codigo=codigo_carteira,
            aluno=self.ra,
            tipo_cartao='Standard',  # Pode ser parametrizado no futuro
            status=True,  # Carteira ativa por padrão
            data_emissao=datetime.now(),
            data_expiracao=datetime.now() + timedelta(days=4*365)
        )
        db.session.add(nova_carteira)
        db.session.commit()

        return True


# Classe responsavel pelo login do usuario
class Login_Usuario:
    def __init__(self, ra, senha):
        self.ra = ra
        self.senha = senha

    def validar_usuario(self):
        """
        Valida se o RA existe no banco de dados.
        Retorna o objeto do usuário se ele for encontrado ou uma mensagem de erro.
        """
        usuario = Tabela_Aluno.query.filter_by(ra=self.ra).first()
        if not usuario:
            return "RA não encontrado."
        return usuario

    def validar_senha(self, senha_hash):
        """
        Valida se a senha fornecida corresponde ao hash armazenado.
        Retorna True se a senha estiver correta, False caso contrário.
        """
        return check_password_hash(senha_hash, self.senha)

    def autenticar(self):
        """
        Realiza a autenticação do usuário.
        - Valida o RA.
        - Valida a senha.
        - Retorna mensagens de sucesso ou erro.
        """
        # Valida o usuário (RA)
        usuario = self.validar_usuario()
        if isinstance(usuario, str):  # Caso seja uma mensagem de erro
            return usuario

        # Valida a senha
        if not self.validar_senha(usuario.senha_hash):
            return "Senha incorreta."

        # Login bem-sucedido
        return f"Login bem-sucedido! Bem-vindo, {usuario.nome}."


# Rodando o aplicativo
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria o banco e tabelas, se ainda não existirem
    app.run(debug=True)  # Inicia o servidor Flask

    """
        # Criar um cadastro de usuário
        cadastro = Cadastro_Usuario(
            nome="João Silva",
            email="joao.silva@email.com",
            ra="123456",
            senha="hashed_password"
        )
        resultado = cadastro.cadastrar_usuario()
        print(resultado)

        # Tentar cadastrar o mesmo RA novamente
        cadastro_repetido = Cadastro_Usuario(
            nome="Maria Oliveira",
            email="maria.oliveira@email.com",
            ra="123456",
            senha="hashed_password2"
        )
        resultado_repetido = cadastro_repetido.cadastrar_usuario()
        print(resultado_repetido)
    
        # Teste com dados corretos
        login = Login_Usuario(ra="123456", senha="hashed_password")
        resultado = login.autenticar()
        print(resultado)  # Ex.: "Login bem-sucedido! Bem-vindo, João Silva."

        # Teste com RA inexistente
        login = Login_Usuario(ra="654321", senha="minhasenha")
        resultado = login.autenticar()
        print(resultado)  # Ex.: "RA não encontrado."

        # Teste com senha incorreta
        login = Login_Usuario(ra="123456", senha="senhaerrada")
        resultado = login.autenticar()
        print(resultado)  # Ex.: "Senha incorreta."
    """