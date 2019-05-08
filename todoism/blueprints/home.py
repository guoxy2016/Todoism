from flask import Blueprint, render_template, current_app, jsonify, make_response
from flask_babel import _
from flask_login import current_user

from ..extensions import db

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    return render_template('index.html')


@home_bp.route('/intro')
def intro():
    return render_template('_intro.html')


@home_bp.route('/set-locale/<locale>')
def set_locale(locale):
    if locale not in current_app.config['TODOISM_LOCALES']:
        return jsonify(message=_('错误的区域')), 404

    response = make_response(jsonify(message=_('设置成功')))
    if current_user.is_authenticated:
        current_user.local = locale
        db.session.commit()
    else:
        response.set_cookie('locale', locale, max_age=60 * 60 * 24 * 30)
    return response

