from flask import Blueprint, request, render_template, redirect, jsonify, url_for
from flask_babel import _
from flask_login import current_user, login_user, logout_user

from ..extensions import db
from ..modles import User, Item

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('todo.app'))
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify(message=_('用户不存在.')), 400
        if not user.validate_password(password):
            return jsonify(message=_('密码错误')), 400
        login_user(user)
        return jsonify(message=_('登陆成功'))
    return render_template('_login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    return jsonify(_('用户已退出'))


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user is not None:
        return jsonify(message=_('用户名已被占用')), 400
    user = User(username=username)
    user.password = password
    item1 = Item(body=_('去看真正的雄伟景色'), author=user)
    item2 = Item(body=_('帮助一位完全陌生的人'), author=user)
    item3 = Item(body=_('在长城上骑自行车'), author=user)
    item4 = Item(body=_('坐在金字塔顶端'), author=user, done=True)
    db.session.add_all([item1, item2, item3, item4])
    db.session.commit()
    return jsonify(message=_('用户创建成功'))
