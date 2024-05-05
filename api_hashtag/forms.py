from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from api_hashtag.models import Usuario


class FormPesquisar(FlaskForm):  # caixa de pesquisa
    pesquisa = StringField("Pesquisar")
    botao_pesquisar = SubmitField("Pesquisar")


class FormLogin(FlaskForm):  # formulário de login
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    botao_login = SubmitField("Login")


class FormCadastro(FlaskForm):  # formulário de cadastro
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 12)])
    confirma_senha = PasswordField("Confirme a senha", validators=[DataRequired(), EqualTo("senha")])
    token = PasswordField("Token", validators=[DataRequired()])
    botao_cadastro = SubmitField("Cadastrar")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            return ValidationError("E-mail já cadastrado")
