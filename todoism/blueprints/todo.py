from flask import Blueprint, render_template, request, jsonify
from flask_babel import _
from flask_login import login_required, current_user

from ..extensions import db
from ..modles import Item

todo_bp = Blueprint('todo', __name__)


@todo_bp.route('/app')
@login_required
def app():
    all_count = Item.query.with_parent(current_user).count()
    active_count = Item.query.with_parent(current_user).filter_by(done=False).count()
    complete_count = Item.query.with_parent(current_user).filter_by(done=True).count()
    return render_template('_app.html', all_count=all_count, active_count=active_count, complate_coun=complete_count,
                           items=current_user.items)


@todo_bp.route('/items/new', methods=['POST'])
@login_required
def new_item():
    data = request.get_json()
    if data is None or data['body'].strip() == '':
        return jsonify(message=_('未获取到内容')), 400
    item = Item(body=data['body'], author=current_user._get_current_object())
    db.session.add(item)
    db.session.commit()
    return jsonify(html=render_template('_item.html', item=item), message='+1')


@todo_bp.route('/item/<int:item_id>/edit', methods=['PUT'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('权限错误')), 403
    data = request.get_json()
    if data is None or data['body'].strip() == '':
        return jsonify(message=_('未获取到内容')), 400
    item.body = data['body']
    db.session.commit()
    return jsonify(message=_('更新成功'))


@todo_bp.route('/item/<int:item_id>/toggle', methods=['PATCH'])
@login_required
def toggle_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('权限错误')), 403
    item.done = not item.done
    db.session.commit()
    return jsonify(message=_('更新成功'))


@todo_bp.route('/item/<int:item_id>/delete', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user != item.author:
        return jsonify(message=_('权限错误')), 403
    db.session.delete(item)
    return jsonify(message=_('删除成功'))


@todo_bp.route('/item/clear', methods=['DELETE'])
@login_required
def clear_items():
    items = Item.query.with_parent(current_user).filter_by(done=True).all()
    for item in items:
        db.session.delete(item)
    db.session.commit()
    return jsonify(message=_('已清理完成条目'))
