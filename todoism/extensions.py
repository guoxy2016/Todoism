from flask import request, current_app
from flask_babel import Babel, _
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(column_0_label)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
login_manager = LoginManager()
csrf = CSRFProtect()
babel = Babel()

login_manager.login_view = 'auth.login'
login_manager.login_message = _('登陆之后才能访问这个页面.')


@login_manager.user_loader
def load_user(user_id):
    from .modles import User
    return User.query.get(int(user_id))


@babel.localeselector
def get_local():
    if current_user.is_authenticated and current_user.locale is not None:
        return current_user.locale
    locale = request.cookies.get('locale')
    if locale is not None:
        return locale
    return request.accept_languages.best_match(current_app.config['TODOISM_LOCALES'])
