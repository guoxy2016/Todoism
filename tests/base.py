from unittest import TestCase

from flask import url_for

from todoism import create_app
from todoism.extensions import db
from todoism.modles import User, Item


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        user = User(username='test_user')
        user.password = '12345678'
        item = Item(body='Test Item', done=False, author=user)
        user2 = User(username='test_user2')
        user2.password = '12345678'
        db.session.add_all([user, item, user2])
        db.session.commit()

    def tearDown(self) -> None:
        db.drop_all()
        self.context.pop()

    def login(self, username='test_user', password='12345678'):
        return self.client.post(url_for('auth.login'), json=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'))

    def get_oauth_token(self, username='test_user', password='12345678'):
        response = self.client.post(url_for('api_v1.token'), data=dict(
            grant_type='password',
            username=username,
            password=password
        ))
        return response.get_json().get('access_token')

    def set_auth_header(self, token):
        return {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
