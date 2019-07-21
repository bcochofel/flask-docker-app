import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Scret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'S3CR3T-K3Y'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
