import os

from flask import Flask, request, render_template, jsonify
from flask_login import current_user

from .blueprints import auth_bp, home_bp, todo_bp
from .extensions import db, login_manager, csrf, babel
from .modles import User, Item


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
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            active_items = Item.query.with_parent(current_user).filter_by(done=False).count()
        else:
            active_items = None
        return dict(active_items=active_items)


def register_errors(app=None):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors.html', code=e.code, info=e.name), e.code

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors.html', code=e.code, info=e.name), e.code

    @app.errorhandler(404)
    def page_not_found(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html or request.path.startswith('/api'):
            response = jsonify(code=e.code, message=e.description)
            response.status_code = 404
            return response
        return render_template('errors.html', code=e.code, info=e.name), e.code

    @app.errorhandler(405)
    def method_not_allowed(e):
        response = jsonify(code=e.code, message=e.description)
        response.status_code = 405
        return response

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html or request.host.startswith('/api'):
            response = jsonify(code=e.code, message=e.description)
            response.status_code = 500
            return response
        return render_template('errors.html', code=e.code, info=e.name), e.code


def register_commands(app=None):
    pass
