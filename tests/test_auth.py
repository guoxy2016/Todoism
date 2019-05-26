from flask import url_for

from todoism.modles import User
from .base import BaseTestCase


class AuthTestCase(BaseTestCase):
    def test_login(self):
        response = self.client.get(url_for('auth.login'), follow_redirects=True)
        self.assertIn('username', response.get_data(as_text=True))
        self.assertIn('password', response.get_data(as_text=True))
        response = self.login()
        self.assertIn('登陆成功', response.get_json().get('message'))
        response = self.login()
        self.assertNotIn('登陆成功', response.get_data(as_text=True))
        self.logout()
        response = self.login('error_username', 'error_password')
        self.assertIn('用户或密码错误', response.get_json().get('message'))
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        self.login()
        response = self.logout()
        self.assertIn('用户已退出', response.get_json().get('message'))

    def test_register(self):
        response = self.client.post(url_for('auth.register'), json=dict(
            username='zhangsan',
            password='12345678'
        ))
        self.assertIn('用户创建成功', response.get_json().get('message'))
        response = self.login('zhangsan')
        self.assertIn('登陆成功', response.get_json().get('message'))
        response = self.client.post(url_for('auth.register'), json=dict(
            username='zhangsan',
            password='12345678'
        ))
        self.assertIn('用户名已被占用', response.get_json().get('message'))
        self.assertIsNotNone(User.query.filter_by(username='zhangsan').first())
