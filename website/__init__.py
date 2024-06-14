from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"
ALLOWED_EXTENSIONS = {'jpg'}


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'M5uFMJ7qc5JHVSA'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .view import view
    from .authentication import authentication

    app.register_blueprint(view, url_prefix='/')
    app.register_blueprint(authentication, url_prefix='/')

    from .model import User, Order, Item

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'authentication.login'
    login_manager.login_message = 'Bejelentkezés szükséges'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists(f'website/{DB_NAME}'):
        db.create_all(app=app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
