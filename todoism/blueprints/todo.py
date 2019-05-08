"""
todo.app                /app
todo.clear_items        /item/clear
todo.delete_item        /item/<int:item_id>/delete
todo.edit_item          /item/<int:item_id>/edit
todo.new_item           /items/new
todo.toggle_item        /item/<int:item_id>/toggle
"""
from flask import Blueprint, render_template

todo_bp = Blueprint('todo', __name__)


@todo_bp.route('/app')
def app():
    return render_template('_app.html')
