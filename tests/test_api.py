from flask import url_for

from todoism.extensions import db
from todoism.modles import Item, User
from .base import BaseTestCase


class ApiV1TestCase(BaseTestCase):
    def test_api_index(self):
        response = self.client.get(url_for('api_v1.index'))
        data = response.get_json()
        self.assertEqual(data['api_version'], '1.0')

    def test_api_get_token(self):
        response = self.client.post(url_for('api_v1.token'), data={
            'grant_type': 'password',
            'username': 'test_user2',
            'password': '12345678'
        })
        data = response.get_json()
        self.assertIn('access_token', data)
        self.assertIn('token_type', data)
        self.assertIn('expires_in', data)
        self.assertEqual('Bearer', data.get('token_type'))

        response = self.client.post(url_for('api_v1.token'), data={
            'grant_type': 'other',
            'username': 'test_user2',
            'password': '12345678'
        })
        data = response.get_json()
        self.assertNotIn('access_token', data)
        self.assertNotIn('token_type', data)
        self.assertNotIn('expires_in', data)
        self.assertIn('The Grant type must be \'password\'', data['message'])

        response = self.client.post(url_for('api_v1.token'), data={
            'grant_type': 'password',
            'username': 'error',
            'password': 'error'
        })
        data = response.get_json()
        self.assertNotIn('access_token', data)
        self.assertNotIn('token_type', data)
        self.assertNotIn('expires_in', data)
        self.assertIn('username or password was invalid', data['message'])

    def test_get_user(self):
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.user'), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get('username'), 'test_user')

    def test_get_item(self):
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.item', item_id=1), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get('kind'), 'Item')
        self.assertEqual(response.get_json().get('body'), 'Test Item')

        token = self.get_oauth_token('test_user2')
        response = self.client.get(url_for('api_v1.item', item_id=1), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 403)
        self.assertIn('Forbidden', response.get_json().get('message'))

    def test_put_item(self):
        token = self.get_oauth_token()
        response = self.client.put(url_for('api_v1.item', item_id=1), headers=self.set_auth_header(token), json={
            'body': 'PUT Item'
        })
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(as_text=True), '')
        item = Item.query.get(1)
        self.assertEqual(item.body, 'PUT Item')

        token = self.get_oauth_token('test_user2')
        response = self.client.put(url_for('api_v1.item', item_id=1), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 403)
        self.assertIn('Forbidden', response.get_json().get('message'))

    def test_patch_item(self):
        token = self.get_oauth_token()
        response = self.client.patch(url_for('api_v1.item', item_id=1), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(as_text=True), '')
        item = Item.query.get(1)
        self.assertTrue(item.done)

        token = self.get_oauth_token('test_user2')
        response = self.client.patch(url_for('api_v1.item', item_id=1), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 403)
        self.assertIn('Forbidden', response.get_json().get('message'))

    def test_delete_item(self):
        token = self.get_oauth_token('test_user2')
        response = self.client.delete(url_for('api_v1.item', item_id=1), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 403)
        self.assertIn('Forbidden', response.get_json().get('message'))

        token = self.get_oauth_token()
        response = self.client.delete(url_for('api_v1.item', item_id=1), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(as_text=True), '')
        item = Item.query.get(1)
        self.assertIsNone(item)

    def test_get_items(self):
        user = User.query.get(1)
        item2 = Item(body='Item test 2', author=user)
        item3 = Item(body='Item test 3', author=user)
        db.session.add_all([item2, item3])
        db.session.commit()
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.items'), headers=self.set_auth_header(token))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual('ItemCollection', data['kind'])
        self.assertEqual(data['count'], 3)

    def test_post_items(self):
        token = self.get_oauth_token()
        response = self.client.post(url_for('api_v1.items'), json={
            'body': 'new post items'
        }, headers=self.set_auth_header(token))
        data = response.get_json()
        self.assertEqual('Item', data['kind'])
        self.assertEqual('new post items', data['body'])

    def test_get_active_items(self):
        user = User.query.get(1)
        item2 = Item(body='Item test 2', author=user)
        item3 = Item(body='Item test 3', author=user)
        item4 = Item(body='Item test 4', done=True, author=user)
        db.session.add_all([item2, item3, item4])
        db.session.commit()
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.active_items'), headers=self.set_auth_header(token))
        data = response.get_json()
        self.assertEqual(data['kind'], 'ItemCollection')
        self.assertEqual(data['count'], 3)

    def test_get_complete_items(self):
        user = User.query.get(1)
        item2 = Item(body='Item test 2', done=True, author=user)
        item3 = Item(body='Item test 3', done=True, author=user)
        item4 = Item(body='Item test 4', done=True, author=user)
        db.session.add_all([item2, item3, item4])
        db.session.commit()
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.complete_items'), headers=self.set_auth_header(token))
        data = response.get_json()
        self.assertEqual(data['kind'], 'ItemCollection')
        self.assertEqual(data['count'], 3)

    def test_delete_complete_items(self):
        user = User.query.get(1)
        item2 = Item(body='Item test 2', author=user)
        item3 = Item(body='Item test 3', done=True, author=user)
        item4 = Item(body='Item test 4', done=True, author=user)
        item5 = Item(body='Item test 5', done=True, author=user)
        db.session.add_all([item2, item3, item4, item5])
        db.session.commit()
        token = self.get_oauth_token()
        response = self.client.delete(url_for('api_v1.complete_items'), headers=self.set_auth_header(token))
        self.assertEqual(response.get_data(as_text=True), '')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Item.query.count(), 2)

