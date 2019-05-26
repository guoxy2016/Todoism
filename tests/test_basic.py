from flask import current_app

from .base import BaseTestCase


class BasicTestCase(BaseTestCase):
    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_app_testing(self):
        self.assertTrue(current_app.testing)

    def test_404(self):
        response = self.client.get('/nothing', follow_redirects=True)
        self.assertIn('The requested URL was not found on the server', response.get_data(as_text=True))
