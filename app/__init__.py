from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)
    with app.app_context():
        app.config.from_object('config')
        db.init_app(app)
        bcrypt.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)
        from .user import user_bp
        from .tourist_places import place_bp
        from .user.models import User
        from .tourist_places.models import Comment, Place, Region, Rating, Type
        app.register_blueprint(user_bp, url_prefix='/auth')
        app.register_blueprint(place_bp, url_prefix='/place')
        db.create_all()
        from app import views
        from app import forms
    return app
