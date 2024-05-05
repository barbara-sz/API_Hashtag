from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
if os.getenv('DATABASE_URL'):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///logs_webhook.db"
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para continuar"
login_manager.login_message_category = "danger"

from api_hashtag import routes
