from api_hashtag import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(db.Model, UserMixin):  # tabela que armazena informações de cadastro para validação de login
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    senha = db.Column(db.String, nullable=False)


class Log(db.Model):  # tabela que armazena informações dos logs de tratativa conforme pgto dos clientes
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String, nullable=False)
    email_cliente = db.Column(db.String, nullable=False)
    status_pgto = db.Column(db.String, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    forma_pgto = db.Column(db.String, nullable=False)
    parcelas = db.Column(db.Integer, nullable=False, default=1)
    id_acao = db.Column(db.Integer, nullable=False)
    desc_acao = db.Column(db.String, nullable=False)
    data_acao = db.Column(db.DateTime, nullable=False, default=datetime.now())
    retorno = db.Column(db.String, nullable=False)
