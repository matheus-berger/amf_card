from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# Formulário de Cadastro
class FormCadastro(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    ra = StringField('RA', validators=[DataRequired(), Length(min=5, max=20)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha', 
                                    validators=[DataRequired(), EqualTo('senha', message="As senhas devem coincidir.")])
    submit = SubmitField('Cadastrar')

# Formulário de Login
class FormLogin(FlaskForm):
    ra = StringField('RA', validators=[DataRequired(), Length(min=5, max=20)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Entrar')
