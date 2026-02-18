from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


class BcryptShim:
    def init_app(self, app):
        return None

    def generate_password_hash(self, password):
        return generate_password_hash(password)

    def check_password_hash(self, pw_hash, password):
        return check_password_hash(pw_hash, password)


bcrypt = BcryptShim()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    from app.routes.auth import auth
    from app.routes.main import main
    from app.routes.compliance import compliance
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(compliance)
    
    with app.app_context():
        db.create_all()
    
    return app