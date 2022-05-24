import os

basedir = os.getcwd()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '27ee859ff7ea825524a952f915814e22420c1a3d2b7bbf143539830bd4620dac'
    RECORDS_PER_PAGE = 2

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir}/test-dev.db'

    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:next23rd@localhost/inventorydb'


config = {'Development': DevelopmentConfig,

        'default': DevelopmentConfig
        }