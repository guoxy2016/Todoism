from flask import url_for

from todoism.modles import Item


def item_schema(item):
    return dict(
        id=item.id,
        self=url_for('.item', item_id=item.id, _external=True),
        kind='Item',
        body=item.body,
        done=item.done,
        author=dict(
            id=item.author_id,
            url=url_for('.user', _external=True),
            username=item.author.username,
            kind='User'
        )
    )


def user_schema(user):
    return dict(
        id=user.id,
        self=url_for('.user', _external=True),
        kind='User',
        username=user.username,
        all_items_url=url_for('.items', _external=True),
        active_items_url=url_for('.active_items', _external=True),
        completed_items_url=url_for('.completed_items', _external=True),
        all_item_count=len(user.items),
        active_item_count=Item.query.with_parent(user).filter_by(done=False).count(),
        completed_item_count=Item.query.with_parent(user).filter_by(done=True).count()
    )


def items_schema(items, end_point, per_page, current, prev, next, pagination):
    return dict(
        self=current,
        kind='ItemCollection',
        items=[item_schema(item) for item in items],
        prev=prev,
        next=next,
        last=url_for(end_point, page=pagination.pages, per_page=per_page, _external=True),
        first=url_for(end_point, page=1, per_page=per_page, _external=True),
        count=pagination.total
    )
