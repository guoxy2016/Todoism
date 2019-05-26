import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Base:
    TODOISM_LOCALES = ['zh', 'en']
    TODOISM_ITEMS_PER_PAGE = 10

    SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key')
    SERVER_NAME = 'todoism.site:8000'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BABEL_DEFAULT_LOCALE = TODOISM_LOCALES[0]


class Development(Base):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'data-dev.db')


class Testing(Base):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class Production(Base):
    SERVER_NAME = 'todoism.com'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///' + os.path.join(BASE_DIR, 'data.db'))


config = {
    'development': Development,
    'testing': Testing,
    'production': Production
}
