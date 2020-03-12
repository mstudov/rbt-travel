from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()
db = SQLAlchemy()
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
