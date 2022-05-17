from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config[config_filename])

    db.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.reimbursed import reimbursed
    app.register_blueprint(reimbursed)

    from app.disbursed import disbursed
    app.register_blueprint(disbursed)
    
    return app