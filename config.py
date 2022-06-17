import os

basedir = os.getcwd()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    RECORDS_PER_PAGE = 20

class DevelopmentConfig(Config):
    # SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir}/test-dev.db'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:next23rd@localhost/inventorydb'


config = {'development': DevelopmentConfig,

        'default': DevelopmentConfig
        }