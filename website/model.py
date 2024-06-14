from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db

user_item = db.Table(
    'user_item',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('quantity', db.Integer, default=1)
)

order_item = db.Table(
    'order_item',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('quantity', db.Integer, default=1)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    address = db.Column(db.String(100))
    added_to_cart = db.relationship('Item', secondary=user_item, backref='items_in_cart')


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_amount = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.localtimestamp())
    is_completed = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    items_bought = db.relationship('Item', secondary=order_item, backref='ordered_items')


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    platform = db.Column(db.String(50))
    price = db.Column(db.Integer)
    img_name = db.Column(db.String(50))
    is_deleted = db.Column(db.Boolean, default=False)
