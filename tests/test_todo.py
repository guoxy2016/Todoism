from flask import url_for

from todoism.extensions import db
from todoism.modles import User, Item
from .base import BaseTestCase


class TodoTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(TodoTestCase, self).setUp()
        self.login()

    def test_app(self):
        response = self.client.get(url_for('todo.app'))
        self.assertIn('接下来计划干点啥', response.get_data(as_text=True))
        self.assertIn('清空', response.get_data(as_text=True))

    def test_new_item(self):
        response = self.client.post(url_for('todo.new_item'), json=dict(
            body='test new item'
        ))
        self.assertIn('test new item', response.get_json().get('html'))
        self.assertIn('+1', response.get_json().get('message'))
        response = self.client.post(url_for('todo.new_item'), json=dict(
            body=''
        ))
        self.assertIsNone(response.get_json().get('html'))
        self.assertNotIn('+1', response.get_json().get('message'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('未获取到内容', response.get_json().get('message'))

    def test_edit_item(self):
        response = self.client.put(url_for('todo.edit_item', item_id=1), json=dict(
            body='edit item'
        ), follow_redirects=True)
        self.assertIn('更新成功', response.get_json().get('message'))
        response = self.client.put(url_for('todo.edit_item', item_id=1), json=dict(
            body=''
        ))
        self.assertIn('未获取到内容', response.get_json().get('message'))
        self.assertEqual(response.status_code, 400)
        self.logout()
        self.login('test_user2')
        response = self.client.put(url_for('todo.edit_item', item_id=1), json=dict(
            body='edit item'
        ))
        self.assertNotIn('更新成功', response.get_json().get('message'))
        self.assertIn('权限错误', response.get_json().get('message'))
        self.assertEqual(response.status_code, 403)

    def test_toggle_item(self):
        response = self.client.patch(url_for('todo.toggle_item', item_id=1))
        self.assertIn('更新成功', response.get_json().get('message'))
        self.logout()
        self.login('test_user2')
        response = self.client.patch(url_for('todo.toggle_item', item_id=1))
        self.assertIn('权限错误', response.get_json().get('message'))
        self.assertEqual(response.status_code, 403)

    def test_delete_item(self):
        self.logout()
        self.login('test_user2')
        response = self.client.delete(url_for('todo.delete_item', item_id=1))
        self.assertIn('权限错误', response.get_json().get('message'))
        self.assertEqual(response.status_code, 403)
        self.logout()
        self.login()
        response = self.client.delete(url_for('todo.delete_item', item_id=1))
        self.assertIn('删除成功', response.get_json().get('message'))

    def test_clear_items(self):
        user = User.query.get(1)
        self.client.patch(url_for('todo.toggle_item', item_id=1))
        item = Item(body='test item 2', done=True, author=user)
        item1 = Item(body='test item 3', done=True, author=user)
        db.session.add_all([item, item1])
        response = self.client.delete(url_for('todo.clear_items'))
        self.assertIn('已清理完成条目', response.get_json().get('message'))
        self.assertEqual(Item.query.with_parent(user).filter_by(done=True).count(), 0)
