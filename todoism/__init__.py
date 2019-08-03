import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

import click
from flask import Flask, request, render_template, jsonify
from flask_login import current_user

from .apis.v1 import api_v1
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
    register_commands(app)

    return app


def register_logging(app=None):
    app.logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - "%(pathname)s", line:%(lineno)s - %(message)s')
    file_handler = RotatingFileHandler('logs/data.log', maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] - "%(remote_addr)s : %(url)s" - %(levelname)s - "%(pathname)s", line:%(lineno)s - %(message)s'
    )

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=app.config['ALBUMY_ADMIN_EMAIL'],
        subject='Albumy程序错误',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    )
    mail_handler.setFormatter(request_formatter)
    mail_handler.setLevel(logging.ERROR)

    if not app.debug:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(mail_handler)


def register_extensions(app=None):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    csrf.exempt(api_v1)
    babel.init_app(app)


def register_blueprint(app=None):
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(todo_bp)
    app.register_blueprint(api_v1, subdomain='api', url_prefix='/v1')


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
        return render_template('errors.html', code=e.code, info=e.description), e.code

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors.html', code=e.code, info=e.description), e.code

    @app.errorhandler(404)
    def page_not_found(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html or request.host.startswith(
                'api'):
            response = jsonify(code=e.code, message=e.description)
            response.status_code = 404
            return response
        return render_template('errors.html', code=e.code, info=e.description), e.code

    @app.errorhandler(405)
    def method_not_allowed(e):
        response = jsonify(code=e.code, message=e.description)
        response.status_code = 405
        return response

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html or request.host.startswith(
                'api'):
            if hasattr(e, 'code') and hasattr(e, 'description'):
                response = jsonify(code=500, message=e.description)
            else:
                response = jsonify(code=500, message='系统错误')
                print(e.args)
            response.status_code = 500
            return response
        return render_template('errors.html', code=500, info='系统错误'), 500


def register_commands(app=None):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='删除后创建')
    def init_db(drop):
        """初始化数据库"""
        if drop:
            click.confirm('这将清空整个数据库, 你确定吗?', abort=True)
            db.drop_all()
            click.echo('数据库清理完毕!')
        click.echo('正在初始化数据库...')
        db.create_all()
        click.echo('Done!')

    @app.cli.group()
    def translate():
        """翻译以及本地化命令"""
        pass

    @translate.command()
    @click.argument('locale')
    def init(locale):
        """初始化新的语言"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('执行extract命令失败')
        if os.system('pybabel init -i messages.pot -d todoism/translations -l ' + locale):
            raise RuntimeError('执行init命令失败')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """更新所有语言"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('执行extract命令失败')
        if os.system('pybabel update -i messages.pot -d todoism/translations'):
            raise RuntimeError('执行update命令失败')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """编译所有语言"""
        if os.system('pybabel compile -d todoism/translations'):
            raise RuntimeError('执行compile命令失败')
