from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config[config_filename])

    db.init_app(app)
    bootstrap.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app