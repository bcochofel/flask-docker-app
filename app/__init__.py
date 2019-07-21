from flask import Flask
from config import config
from flask_misaka import Misaka

md = Misaka(hard_wrap=True, tables=True)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    md.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
