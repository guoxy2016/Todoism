import os

from flask import Flask

from .extensions import db, login_manager, csrf, babel
from .modles import User, Item
from .blueprints import auth_bp, home_bp, todo_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG')
    app = Flask('todoism')
    from .setting import config
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprint(app)
    register_shell_context(app)
    register_template_context(app)
    register_errors(app)

    return app


def register_logging(app=None):
    pass


def register_extensions(app=None):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app)


def register_blueprint(app=None):
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(todo_bp)


def register_shell_context(app=None):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Item=Item)


def register_template_context(app=None):
    pass


def register_errors(app=None):
    pass


def register_commands(app=None):
    pass
