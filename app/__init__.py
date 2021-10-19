import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'SQLALCHEMY_DATABASE_URI')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get(
        'SQLALCHEMY_TRACK_MODIFICATIONS')

    # app.config['TEMPLATES_AUTO_RELOAD'] = os.environ.get(
    #     'TEMPLATES_AUTO_RELOAD')
    # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = os.environ.get(
    #     'SEND_FILE_MAX_AGE_DEFAULT')

    login_manager.init_app(app)
    login_manager.login_message = "Access Denied!, Log in to proceed"
    login_manager.login_view = "auth.login"

    db.init_app(app)
    migrate = Migrate(app, db, compare_type=True)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for agora
    from .agora import agora as agora_blueprint
    app.register_blueprint(agora_blueprint)

    from .agora_rtm import agora_rtm as agora_rtm_blueprint
    app.register_blueprint(agora_rtm_blueprint)

    return app
