from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    _password_hash = db.Column(db.String(128))
    locale = db.Column(db.String(20), )
    items = db.relationship('Item', back_populates='author', cascade='all')

    @property
    def password(self):
        raise AttributeError('Not Readable!')

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self._password_hash, password)

    def __repr__(self):
        return '<User: %r>' % self.username


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='items')
