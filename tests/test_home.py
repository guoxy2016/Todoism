from flask import url_for

from .base import BaseTestCase


class HomeTestCase(BaseTestCase):
    def test_index(self):
        response = self.client.get(url_for('home.index'))
        self.assertIn('Todoism', response.get_data(as_text=True))

    def test_intro(self):
        response = self.client.get(url_for('home.intro'))
        self.assertIn('我们是有规划的人', response.get_data(as_text=True))

    def test_set_locale(self):
        response = self.client.get(url_for('home.set_locale', locale='no-locale'))
        self.assertIn('错误的区域', response.get_json().get('message'))
        self.assertEqual(response.status_code, 404)
        self.client.get(url_for('home.set_locale', locale='en'))
        response = self.client.get(url_for('home.intro'))
        self.assertIn('We are todoist, we use todoism', response.get_data(as_text=True))
        self.client.get(url_for('home.set_locale', locale='zh'))
        response = self.client.get(url_for('home.intro'))
        self.assertIn('我们是有规划的人', response.get_data(as_text=True))
