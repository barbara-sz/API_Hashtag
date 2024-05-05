from flask import render_template, url_for, redirect, request, jsonify, make_response, flash
from api_hashtag import app, db, bcrypt
from flask_login import login_required, login_user, logout_user
from api_hashtag.forms import FormLogin, FormCadastro, FormPesquisar
from api_hashtag.models import Usuario, Log
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TOKEN')


@app.route("/", methods=["GET", "POST"])  # tela de consulta de clientes
@login_required
def consulta():
    page = request.args.get('page', 1, type=int)
    tabela = db.select(Log).order_by(Log.id)
    tabela_paginada = db.paginate(tabela, page=page, per_page=10, error_out=False)
    form_pesquisa = FormPesquisar()
    pesquisado = form_pesquisa.pesquisa.data
    prox = url_for('consulta', page=tabela_paginada.next_num) \
        if tabela_paginada.has_next else None
    ant = url_for('consulta', page=tabela_paginada.prev_num) \
        if tabela_paginada.has_prev else None

    if pesquisado and "botao_pesquisar" in request.form:
        tabela_paginada = db.paginate(db.select(Log).order_by(Log.id).filter_by(email_cliente=pesquisado),
                                          page=page, per_page=20, error_out=False)

        if len(list(tabela_paginada)) > 0:
            return render_template("consulta.html", tabela_paginada=tabela_paginada, form=form_pesquisa)
        else:
            flash("E-mail não consta no banco de dados.", 'alert-danger')

    return render_template("consulta.html", form=form_pesquisa, tabela_paginada=tabela_paginada,
                           prox=prox, ant=ant)


@app.route("/cadastro", methods=["GET", "POST"])  # cadastro
def cadastro():
    form_cadastro = FormCadastro()
    token_informado = form_cadastro.token.data
    email = form_cadastro.email.data
    if Usuario.query.filter_by(email=email).first() and "botao_cadastro" in request.form:
        flash("E-mail já cadastrado. Faça login para continuar.", 'alert-danger')
    elif form_cadastro.validate_on_submit() and token_informado == token:
        senha = bcrypt.generate_password_hash(form_cadastro.senha.data).decode("utf-8")
        usuario = Usuario(email=email, senha=senha)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("consulta"))
    elif "botao_cadastro" in request.form and form_cadastro.confirma_senha.data != form_cadastro.senha.data:
        flash("Campos de senha precisam ser iguais!", 'alert-danger')
    elif "botao_cadastro" in request.form and token_informado != token:
        flash("Token informado não é válido!", 'alert-danger')
    return render_template("cadastro.html", form=form_cadastro)


@app.route("/login", methods=["GET", "POST"])  # login
def login():
    form_login = FormLogin()
    next = request.args.get('?next=%2F')
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=True)
            return redirect(url_for("consulta"))
        else:
            flash("Senha e/ou e-mail inválidos!", 'alert-danger')
    return render_template("login.html", form=form_login, next=next)


@app.route("/logout")  # logout
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/api", methods=["GET", "POST"])  # api recebe webhook, executa e devolve a ação e registra no banco de dados
def api():
    # capturar os dados
    webhook = request.json
    nome_cliente = webhook['nome']
    email_cliente = webhook['email']
    status_pgto = webhook['status']
    valor = webhook['valor']
    forma_pgto = webhook['forma_pagamento']
    parcelas = webhook['parcelas']

    # associar tratativa de acordo com status
    if status_pgto == 'aprovado':
        id_acao = 1
        desc_acao = "Acesso liberado e mensagem de boas-vindas enviada."
        retorno = "Liberar acesso ao cliente e mandar mensagem de boas-vindas para o e-mail"
    elif status_pgto == 'reprovado':
        id_acao = 2
        desc_acao = "Enviada mensagem de pagamento reprovado para o e-mail."
        retorno = "Enviar mensagem de pagamento reprovado para o e-mail"
    elif status_pgto == 'reembolsado':
        id_acao = 3
        desc_acao = "Acesso ao portal retirado do cliente."
        retorno = "Retirar acesso ao portal do cliente."
    else:
        id_acao = 4
        desc_acao = "Tratativa pendente. Status de pagamento não identificado."
        retorno = "Tratativa pendente. Verificar"

    # salvar informações no banco de dados
    log = Log(nome_cliente=nome_cliente, email_cliente=email_cliente, status_pgto=status_pgto, valor=valor,
              forma_pgto=forma_pgto, parcelas=parcelas, id_acao=id_acao, desc_acao=desc_acao, retorno=retorno)
    db.session.add(log)
    db.session.commit()

    # retornar o que foi/deve ser feito
    if id_acao < 3:
        mensagem = str(Log.query.filter_by(id_acao=id_acao).first().retorno) + ' ' + email_cliente + '.'
    elif id_acao == 4:
        mensagem = str(Log.query.filter_by(id_acao=id_acao).first().retorno) + ' LOG ID ' + str(Log.id) + '.'
    else:
        mensagem = str(Log.query.filter_by(id_acao=id_acao).first().retorno)
    return make_response(jsonify(mensagem))
