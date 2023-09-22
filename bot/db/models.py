import json

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = sa.Column(sa.BigInteger, primary_key=True)
    username = sa.Column(sa.Text, nullable=True)
    params = sa.Column(sa.JSON, nullable=True)
    notice = sa.Column(sa.JSON, nullable=True)
    # notice = {
    #     'move': {
    #         'target_store': [], 'source_store': [], 'article': [],
    #         'text': ['sum', 'quantity', 'articles_text', 'source_store', 'target_store', 'description', 'positions'],
    #         #'positions': ['article', 'size', 'name', 'quantity', 'price']
    #     },
    #     'supply': {
    #         'agent': [], 'target_store': [], 'article': [],
    #         'text': ['sum', 'quantity', 'articles_text', 'target_store', 'description', 'agent', 'positions'],
    #         'positions': ['article', 'size', 'name', 'quantity', 'price']
    #     },
    #     'purchaseorder': {
    #         'agent': [], 'target_store': [], 'article': [], 'days': [],
    #         'text': ['sum', 'quantity', 'articles_text', 'target_store', 'description', 'agent', 'positions'],
    #         'positions': ['article', 'size', 'name', 'quantity', 'price']
    #     },
    #     'productiontask': {
    #         'material_store': [],  'article': [], 'days': [],
    #         'text': ['sum', 'plan_quantity', 'produced_quantity', 'articles_text', 'material_store', 'description', 'positions'],
    #         'positions': ['article', 'size', 'name', 'plan_quantity', 'produced_quantity', 'price']
    #     },
    #     'other': {
    #         'out_stock': ['count_size', 'count_sizes', 'count_article'],
    #         'oborot': {
    #             'days_in_store': []
    #         }
    #     }
    # }
    # notice_default = {
    #     'move': None,
    #     'supply': None,
    #     'purchaseorder': None,
    #     'productiontask': None,
    #     'other': None,
    # }

    def __repr__(self):
        j = {'user_id': self.user_id, 'username': self.username,
             'params': self.params, 'notice': self.notice}
        return json.dumps(j)


class Agent(Base):
    __tablename__ = 'agents'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    name = sa.Column(sa.Text, nullable=True)
    meta = sa.Column(sa.JSON)

    def __repr__(self):
        j = {'id': self.id, 'name': self.name,
             'meta': self.meta, }
        return json.dumps(j)


class Store(Base):
    __tablename__ = 'stores'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    name = sa.Column(sa.Text)
    is_fabric = sa.Column(sa.Boolean, default=False)
    color = sa.Column(sa.Text, nullable=True)

    def __repr__(self):
        j = {'id': self.id, 'name': self.name,
             'is_fabric': self.is_fabric, 'color': self.color}
        return json.dumps(j)


class Product(Base):
    __tablename__ = 'products'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    uid = sa.Column(sa.VARCHAR(100))
    code = sa.Column(sa.Text, nullable=True)
    article = sa.Column(sa.Text, nullable=True)
    name = sa.Column(sa.Text, nullable=True)
    description = sa.Column(sa.Text, nullable=True)
    buy_price = sa.Column(sa.Float, nullable=True)
    sell_price = sa.Column(sa.Float, nullable=True)
    images = sa.Column(sa.ARRAY(sa.Text), nullable=True)
    videos = sa.Column(sa.ARRAY(sa.Text), nullable=True)
    barcodes = sa.Column(sa.ARRAY(sa.JSON), nullable=True)
    meta = sa.Column(sa.JSON)
    variants = relationship('Variant')

    def __repr__(self):
        j = {
            'id': self.id, 'uid': self.uid, 'code': self.code,
            'article': self.article, 'name': self.name,
            'description': self.description, 'buy_price': self.buy_price,
            'sell_price': self.sell_price, 'images': self.images,
            'videos': self.videos, 'barcodes': self.barcodes,
            'meta': self.meta, 'variants': json.loads(str(self.variants)),

        }
        return json.dumps(j)


class Variant(Base):
    __tablename__ = 'variants'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    uid = sa.Column(sa.VARCHAR(100))
    code = sa.Column(sa.Text, nullable=True)
    size = sa.Column(sa.Text, nullable=True)
    barcodes = sa.Column(sa.ARRAY(sa.JSON), nullable=True)
    meta = sa.Column(sa.JSON)
    product = sa.Column(sa.VARCHAR(100), sa.ForeignKey('products.id'))

    def __repr__(self):
        j = {
            'id': self.id, 'uid': self.uid, 'code': self.code,
            'size': self.size, 'barcodes': self.barcodes,
            'meta': self.meta, 'product': self.product,

        }
        return json.dumps(j)


class Currency(Base):
    __tablename__ = 'currencies'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    name = sa.Column(sa.Text, nullable=True)
    fullName = sa.Column(sa.Text, nullable=True)
    rate = sa.Column(sa.Float, default=1)
    isoCode = sa.Column(sa.Text, nullable=True)

    def __repr__(self):
        j = {
            'id': self.id, 'name': self.name, 'fullName': self.fullName,
            'rate': self.rate, 'isoCode': self.isoCode,
        }
        return json.dumps(j)


class Status(Base):
    __tablename__ = 'statuses'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    name = sa.Column(sa.Text, nullable=True)

    def __repr__(self):
        j = {
            'id': self.id, 'name': self.name,
        }
        return json.dumps(j)


class ProductionTask(Base):
    __tablename__ = 'production_tasks'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    applicable = sa.Column(sa.Boolean)
    name = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    moment = sa.Column(sa.DateTime)
    production_start = sa.Column(sa.DateTime, nullable=True)
    production_end = sa.Column(sa.DateTime, nullable=True)
    delivery_planned = sa.Column(sa.DateTime, nullable=True)
    materials_store_id = sa.Column(sa.VARCHAR(100))
    products_store_id = sa.Column(sa.VARCHAR(100))
    period_delivery = sa.Column(sa.Integer)
    state = sa.Column(sa.JSON, nullable=True)
    positions = sa.Column(sa.ARRAY(sa.JSON))
    edited = sa.Column(sa.ARRAY(sa.Text))

    def __repr__(self):
        j = {
            'id': self.id, 'applicable': self.applicable,
            'name': self.name, 'description': self.description,
            'moment': str(self.moment), 'production_start': str(self.production_start),
            'production_end': str(self.production_end), 'delivery_planned': str(self.delivery_planned),
            'materials_store_id': self.materials_store_id, 'products_store_id': self.products_store_id,
            'period_delivery': self.period_delivery,
            'state': self.state, 'positions': self.positions, 'edited': self.edited,
        }
        return json.dumps(j)


class Move(Base):
    __tablename__ = 'moves'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    applicable = sa.Column(sa.Boolean)
    name = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    moment = sa.Column(sa.DateTime)
    source_store_id = sa.Column(sa.VARCHAR(100))
    target_store_id = sa.Column(sa.VARCHAR(100))
    positions = sa.Column(sa.ARRAY(sa.JSON))
    amount = sa.Column(sa.Float)
    currency_id = sa.Column(sa.VARCHAR(100))
    state = sa.Column(sa.JSON, nullable=True)
    edited = sa.Column(sa.ARRAY(sa.Text))

    def __repr__(self):
        j = {
            'id': self.id, 'applicable': self.applicable,
            'name': self.name, 'description': self.description,
            'moment': str(self.moment), 'source_store_id': self.source_store_id,
            'target_store_id': self.target_store_id, 'positions': self.positions,
            'amount': self.amount, 'currency_id': self.currency_id,
            'state': self.state, 'edited': self.edited,

        }
        return json.dumps(j)


class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    applicable = sa.Column(sa.Boolean)
    name = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    moment = sa.Column(sa.DateTime)
    delivery_planned = sa.Column(sa.DateTime, nullable=True)
    agent_id = sa.Column(sa.VARCHAR(100))
    target_store_id = sa.Column(sa.VARCHAR(100), nullable=True)
    positions = sa.Column(sa.ARRAY(sa.JSON))
    amount = sa.Column(sa.Float)
    currency_id = sa.Column(sa.VARCHAR(100))
    state = sa.Column(sa.JSON, nullable=True)
    edited = sa.Column(sa.ARRAY(sa.Text))

    def __repr__(self):
        j = {
            'id': self.id, 'applicable': self.applicable,
            'name': self.name, 'description': self.description,
            'moment': str(self.moment), 'delivery_planned': str(self.delivery_planned), 'agent_id': self.agent_id,
            'target_store_id': self.target_store_id, 'positions': self.positions,
            'amount': self.amount, 'currency_id': self.currency_id,
            'state': self.state, 'edited': self.edited,
        }
        return json.dumps(j)


class Supply(Base):
    __tablename__ = 'supplies'
    id = sa.Column(sa.VARCHAR(100), primary_key=True)
    applicable = sa.Column(sa.Boolean)
    name = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    moment = sa.Column(sa.DateTime)
    agent_id = sa.Column(sa.VARCHAR(100))
    target_store_id = sa.Column(sa.VARCHAR(100))
    positions = sa.Column(sa.ARRAY(sa.JSON))
    state = sa.Column(sa.JSON, nullable=True)
    amount = sa.Column(sa.Float)
    currency_id = sa.Column(sa.VARCHAR(100))
    purchase_order_id = sa.Column(sa.VARCHAR(100), nullable=True)
    edited = sa.Column(sa.ARRAY(sa.Text))

    def __repr__(self):
        j = {
            'id': self.id, 'applicable': self.applicable,
            'name': self.name, 'description': self.description,
            'moment': str(self.moment), 'agent_id': self.agent_id,
            'target_store_id': self.target_store_id, 'positions': self.positions,
            'state': self.state,
            'amount': self.amount, 'currency_id': self.currency_id,
            'purchase_order_id': self.purchase_order_id, 'edited': self.edited,

        }
        return json.dumps(j)
