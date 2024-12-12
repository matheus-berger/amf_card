# Importando as bibliotecas necessarias
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import random

# Criando o Aplicativo Flask
app = Flask(__name__)

# Criando a estrutura do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/amf_card.db'
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

    def validar_ra(self):
        # Verificar se o RA já existe no banco
        aluno_existente = Tabela_Aluno.query.filter_by(ra=self.ra).first()
        if aluno_existente:
            return f"O RA {self.ra} já está cadastrado."
        return None

    def cadastrar_usuario(self):
        # Validar RA
        mensagem = self.validar_ra()
        if mensagem:
            return mensagem

        # Criar o aluno
        novo_aluno = Tabela_Aluno(
            ra=self.ra,
            nome=self.nome,
            email=self.email,
            senha_hash=self.senha  # Aqui você pode implementar hash de senha
        )
        db.session.add(novo_aluno)
        db.session.commit()

        # Cadastrar a carteira
        cadastro_carteira = Cadastro_Carteira(self.ra)
        if cadastro_carteira.cadastrar():
            return f"Usuário {self.nome} cadastrado com sucesso!"
        else:
            return "Erro ao cadastrar a carteira do usuário."


# Classe responsavel pelo cadastro da Carteira
class Cadastro_Carteira:
    def __init__(self, ra):
        self.ra = ra

    # Método para cadastrar carteira
    def cadastrar(self, ra):
        if ra is not None:
            return True
        else: 
            return None