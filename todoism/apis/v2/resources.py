from flask import jsonify, request, url_for, g, current_app
from flask.views import MethodView

from todoism.extensions import db
from todoism.modles import Item, User
from . import api_v2
from .auth import generate_token, auth_required
from .errors import ValidationError, api_abort
from .schemas import item_schema, items_schema, user_schema


def get_item_body():
    data = request.get_json()
    body = data.get('body')
    if body is None or str(body).strip() == '':
        raise ValidationError('消息内容为空')
    return body


class IndexAPI(MethodView):
    def get(self):
        """获取基本资源"""
        return jsonify(
            api_version='1.0',
            api_base_url=url_for('.index', _external=True),
            current_user_url=url_for('.user', _external=True),
            authentication_url=url_for('.token', _external=True),
            item_url='http://api.todoism.dev.com:8000/v1/user/items/{item_id}',
            current_user_items_url=url_for('.items', _external=True),
            current_user_active_items_url=url_for('.active_items', _external=True),
            current_user_completed_items_url=url_for('.active_items', _external=True)
        )


class AuthTokenAPI(MethodView):
    def post(self):
        """获取验证token"""
        grant_type = request.form.get('grant_type')
        username = request.form.get('username')
        password = request.form.get('password')

        if grant_type is None or grant_type != 'password':
            return api_abort(400, 'The Grant type must be \'password\'.')
        user = User.query.filter_by(username=username)
        if user is None or not user.validate_password(password):
            return api_abort(400, 'username or password was invalid')
        token, expiration = generate_token(user)

        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.header['Cache-Control'] = 'no-store'
        response.header['Pragma'] = 'no-cache'
        return response


class UserAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        return jsonify(user_schema(g.current_user))


class ItemAPI(MethodView):
    decorators = [auth_required]

    def get(self, item_id):
        """获取条目"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        return jsonify(item_schema(item))

    def put(self, item_id):
        """修改条目"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.body = get_item_body()
        db.session.commit()
        return '', 204

    def patch(self, item_id):
        """切换完成状态"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        item.done = not item.done
        db.session.commit()
        return '', 204

    def delete(self, item_id):
        """删除条目"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api_abort(403)
        db.session.delete(item)
        db.session.commit()
        return '', 204


class ItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """获取所有条目"""
        page = request.args.get('page', 1, int)
        per_page = request.args.get('per_page', current_app.config['TODOISM_ITEMS_PER_PAGE'], int)
        pagination = Item.query.with_parent(g.current_user).order_by(Item.timestamp.desc()).paginate(page, per_page)
        items = pagination.items
        current = url_for('.items', page=page, per_page=per_page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.items', page=page - 1, per_page=per_page, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.items', page=page + 1, per_page=per_page, _external=True)
        return jsonify(items_schema(items, '.items', per_page, current, prev, next, pagination))

    def post(self):
        """创建新条目"""
        item = Item(body=get_item_body(), author=g.current_user)
        db.session.add(item)
        db.session.commit()
        response = jsonify(item_schema(item))
        response.status_code = 201
        response.headers['Location'] = url_for('.item', item_id=item.id, _external=True)
        return response


class ActiveItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """获取所有未完成的条目"""
        page = request.args.get('page', 1, int)
        per_page = request.args.get('per_page', current_app.config['TODOISM_ITEMS_PER_PAGE'], int)
        pagination = Item.query.with_parent(g.current_user).filter_by(done=False).order_by(
            Item.timestamp.desc()).paginate(page, per_page)
        items = pagination.items
        current = url_for('.active_items', page=page, per_page=per_page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.active_items', page=page - 1, per_page=per_page, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.active_items', page=page + 1, per_page=per_page, _external=True)
        return jsonify(items_schema(items, '.active_items', per_page, current, prev, next, pagination))


class CompletedItemAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """获取所有已完成的条目"""
        page = request.args.get('page', 1, int)
        per_page = request.args.get('per_page', current_app.config['TODOISM_ITEMS_PER_PAGE'], int)
        pagination = Item.query.with_parent(g.current_user).filter_by(done=False).order_by(
            Item.timestamp.desc()).paginate(page, per_page)
        items = pagination.items
        current = url_for('.complete_items', page=page, per_page=per_page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.complete_items', page=page - 1, per_page=per_page, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.complete_items', page=page + 1, per_page=per_page, _external=True)
        return jsonify(items_schema(items, '.complete_items', per_page, current, prev, next, pagination))

    def delete(self):
        """删除所有完成条目"""
        Item.query.with_parent(g.current_user).filter_by(done=True).delete()
        db.session.commit()
        return '', 204


api_v2.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v2.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])
api_v2.add_url_rule('/user', view_func=UserAPI.as_view('user'))
api_v2.add_url_rule('/user/items', view_func=ItemsAPI.as_view('items'))
api_v2.add_url_rule('/user/items/<int:item_id>', view_func=ItemAPI.as_view('item'))
api_v2.add_url_rule('/user/items/active', view_func=ActiveItemsAPI.as_view('active_items'))
api_v2.add_url_rule('/user/items/active', view_func=CompletedItemAPI.as_view('complete_items'))

from webargs import fields, validate
from webargs.flaskparser import parser, use_args

user_args = {
    'username': fields.Str(required=True),
    'password': fields.Str(validate=validate.Length(min=6)),
    # 'display_per_page': fields.Int(missing=10)
}


@api_v2.route('/register', methods=['POST'])
@use_args(user_args)
def register(args):
    user = User(username=args['username'])
    user.password = args['password']
    db.session.add(user)
    db.session.commit()
    return '注册成了'
