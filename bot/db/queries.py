import datetime
import json

import sqlalchemy as sa
from db.db_connect import Session
from db.models import User, Move, Supply, ProductionTask, PurchaseOrder, Product, Variant, Store, Agent, Currency, \
    Status


def get_id_by_meta(x):
    return x['meta']['href'].split('/')[-1]


class DBUser:

    @classmethod
    def add(cls, session: Session, args: dict):
        print('add_user', args)
        notice_default = {
            'move': {
                'turn_on': True,
                'send_new': True,
                'send_updated': False,
                'applicable': True,
                'target_store': [], 'source_store': [], 'article': [],
                'text': ['sum', 'quantity', 'articles_text', 'source_store', 'target_store', 'description'],
                'positions': ['article', 'size', 'name', 'quantity', 'price']
            },
            'supply': {
                'turn_on': True,
                'send_new': True,
                'send_updated': False,
                'applicable': True,
                'agent': [], 'target_store': [], 'article': [],
                'text': ['sum', 'quantity', 'articles_text', 'target_store', 'description', 'agent'],
                'positions': ['article', 'size', 'name', 'quantity', 'price']
            },
            'purchaseorder': {
                'turn_on': True,
                'send_new': True,
                'send_updated': False,
                'applicable': True,
                'agent': [], 'target_store': [], 'article': [], 'days': [],
                'text': ['sum', 'quantity', 'articles_text', 'target_store', 'description', 'agent'],
                'positions': ['article', 'size', 'name', 'quantity', 'price']
            },
            'productiontask': {
                'turn_on': True,
                'send_new': True,
                'send_updated': False,
                'applicable': True,
                'material_store': [],  'article': [], 'days': [],
                'text': ['sum', 'quantity', 'produced_quantity', 'articles_text', 'material_store', 'description'],
                'positions': ['article', 'size', 'name', 'plan_quantity', 'produced_quantity', 'price']
            },
            'other': {
                'out_stock': ['count_size', 'count_sizes', 'count_article'],
                'oborot': {
                    'days_in_store': []
                }
            }
        }
        user = User(user_id=args['user_id'],
                    username=args.get('username'),
                    params=args.get('params', {}),
                    notice=notice_default,
                    )
        session.add(user)

    @classmethod
    def get(cls, session: Session, user_id: int) -> User:
        print('get_user')
        return session.query(User).where(User.user_id == user_id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[User]:
        return session.query(User).all()

    @classmethod
    def update(cls, session: Session, args: dict):
        print('update_user')
        user = cls.get(session, args['user_id'])
        session.execute(sa.update(User).where(User.user_id == args['user_id']).values(
            username=args.get('username', user.username),
            params=args.get('params', user.params),
            notice=args.get('notice', user.notice),
        ))

    @classmethod
    def update_notice(cls, session: Session, args: dict):
        print('update_user')
        session.execute(sa.update(User).where(User.user_id == args['user_id']).values(
            notice=args['notice'],
        ))

    @classmethod
    def remove(cls, session: Session, user_id):
        session.execute(sa.delete(User).where(User.user_id == user_id))


class DBProduct:

    @classmethod
    def add(cls, session: Session, args: dict):
        product = Product(
            id=args['id'], uid=args['meta']['uuidHref'].split('id=')[1],
            code=args.get('code'), article=args.get('article'),
            name=args.get('name'), description=args.get('description'),
            buy_price=args['buyPrice']['value'] if args.get('buyPrice') else 0,
            sell_price=args['salePrices'][0]['value'] if args.get('salePrices') else 0,
            images=[], videos=[],
            barcodes=args.get('barcodes'),
            meta=args['meta'],
        )
        session.add(product)

    @classmethod
    def get(cls, session: Session, id: str) -> Product:
        return session.query(Product).where(Product.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[Product]:
        return session.query(Product).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        product = cls.get(session, args['id'])
        if not product:
            cls.add(session, args)
            return
        session.execute(sa.update(Product).where(Product.id == args['id']).values(
            uid=args['meta']['uuidHref'].split('id=')[1],
            code=args.get('code'), article=args.get('article'),
            name=args.get('name'), description=args.get('description'),
            buy_price=args['buyPrice']['value'] if args.get('buyPrice') else 0,
            sell_price=args['salePrices'][0]['value'] if args.get('salePrices') else 0,
            images=[], videos=[],
            barcodes=args.get('barcodes'),
            meta=args['meta'],
        ))

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(Product).where(Product.id == id))


class DBVariant:

    @classmethod
    def add(cls, session: Session, args: dict):
        size = None
        if args.get('characteristics'):
            for i in args['characteristics']:
                if i['name'] == 'размер':
                    size = i['value']
        variant = Variant(
            id=args['id'], uid=args['meta']['uuidHref'].split('id=')[1],
            code=args.get('code'), size=size,
            barcodes=args.get('barcodes'),
            meta=args['meta'],
            product=get_id_by_meta(args['product']) if args.get('product') else None,
        )
        session.add(variant)

    @classmethod
    def get(cls, session: Session, id: str) -> Variant:
        return session.query(Variant).where(Variant.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[Variant]:
        return session.query(Variant).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        variant = cls.get(session, args['id'])
        if not variant:
            cls.add(session, args)
            return
        size = None
        if args.get('characteristics'):
            for i in args['characteristics']:
                if i['name'] == 'размер':
                    size = i['value']
        session.execute(sa.update(Variant).where(Variant.id == args['id']).values(
            uid=args['meta']['uuidHref'].split('id=')[1],
            code=args.get('code'), size=size,
            barcodes=args.get('barcodes'),
            meta=args['meta'],
            product=get_id_by_meta(args['product']) if args.get('product') else None,
        ))

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(Variant).where(Variant.id == id))


class DBStore:

    @classmethod
    def add(cls, session: Session, args: dict):
        store = Store(
            id=args['id'],
            name=args.get('name'),
            is_fabric=False,
            color='#B64D37',
        )
        session.add(store)

    @classmethod
    def get(cls, session: Session, id: str) -> Store:
        return session.query(Store).where(Store.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[Store]:
        return session.query(Store).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        store = cls.get(session, args['id'])
        if not store:
            cls.add(session, args)
            return
        session.execute(sa.update(Store).where(Store.id == args['id']).values(
            name=args.get('name'),
            is_fabric=False,
            color='#B64D37',
        ))

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(Store).where(Store.id == id))


class DBAgent:

    @classmethod
    def add(cls, session: Session, args: dict):
        agent = Agent(
            id=args['id'],
            name=args.get('name'),
            meta=args.get('meta')
        )
        session.add(agent)

    @classmethod
    def get(cls, session: Session, id: str) -> Agent:
        return session.query(Agent).where(Agent.id == id).one_or_none()

    @classmethod
    def get_by_name(cls, session: Session, name: str) -> Agent:
        agents = cls.get_all(session)
        return [i for i in agents if name in i.name.lower()]

    @classmethod
    def get_all(cls, session: Session) -> list[Agent]:
        return session.query(Agent).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        agent = cls.get(session, args['id'])
        if not agent:
            cls.add(session, args)
            return
        session.execute(sa.update(Agent).where(Agent.id == args['id']).values(
            name=args.get('name'),
            meta=args.get('meta')
        ))

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(Agent).where(Agent.id == id))


class DBCurrency:

    @classmethod
    def add(cls, session: Session, args: dict):

        currency = Currency(
            id=args['id'],
            name=args.get('name'),
            fullName=args.get('fullName'),
            rate=args.get('rate', 1),
            isoCode=args.get('isoCode'),
        )
        session.add(currency)

    @classmethod
    def get(cls, session: Session, id: str) -> Currency:
        return session.query(Currency).where(Currency.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[Currency]:
        return session.query(Currency).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        currency = cls.get(session, args['id'])
        if not currency:
            cls.add(session, args)
            return
        session.execute(sa.update(Currency).where(Currency.id == args['id']).values(
            name=args.get('name'),
            fullName=args.get('fullName'),
            rate=args.get('rate', 1),
            isoCode=args.get('isoCode'),
        ))

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(Currency).where(Currency.id == id))


class DBStatus:

    @classmethod
    def add(cls, session: Session, args: dict):
        status = Status(
            id=args['id'],
            name=args.get('name'),
        )
        session.add(status)

    @classmethod
    def get(cls, session: Session, id: str) -> Status:
        return session.query(Status).where(Status.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[Status]:
        return session.query(Status).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        status = cls.get(session, args['id'])
        if not status:
            cls.add(session, args)
            return
        session.execute(sa.update(Status).where(Status.id == args['id']).values(
            name=args.get('name'),
        ))

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(Status).where(Status.id == id))


class DBProductionTask:

    @classmethod
    def add(cls, session: Session, args: dict):
        period_delivery = 0
        if args.get('attributes'):
            for i in args['attributes']:
                if i['name'] == 'Период поставки':
                    period_delivery = i['value']
                    break
        production_task = ProductionTask(
            id=args['id'], applicable=args['applicable'],
            name=args['name'], description=args.get('description', ''),
            moment=args['moment'].split('.')[0],
            production_start=args.get('productionStart'),
            production_end=args.get('productionEnd'),
            delivery_planned=args.get('deliveryPlannedMoment'),
            materials_store_id=get_id_by_meta(args['materialsStore']),
            products_store_id=get_id_by_meta(args['productsStore']),
            period_delivery=period_delivery,
            positions=args['positions'],
            state=args.get('state'), edited=[],
        )
        session.add(production_task)

    @classmethod
    def get(cls, session: Session, id: str) -> ProductionTask:
        return session.query(ProductionTask).where(ProductionTask.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[ProductionTask]:
        return session.query(ProductionTask).all()

    @classmethod
    def get_by_start_date(cls, session: Session, start_date) -> list[ProductionTask]:
        return session.query(ProductionTask).where(start_date <= ProductionTask.delivery_planned).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        production_task = cls.get(session, args['id'])
        if not production_task:
            cls.add(session, args)
            return True
        period_delivery = 0
        if args.get('attributes'):
            for i in args['attributes']:
                if i['name'] == 'Период поставки':
                    period_delivery = i['value']
                    break
        production_task = json.loads(str(production_task))
        edited_els = [{'db_name': 'applicable', 'doc_name': 'applicable'},
                  {'db_name': 'name', 'doc_name': 'name'},
                  {'db_name': 'description', 'doc_name': 'description'},
                  {'db_name': 'production_start', 'doc_name': 'productionStart'},
                  {'db_name': 'delivery_planned', 'doc_name': 'deliveryPlannedMoment'},
                  {'db_name': 'materials_store_id', 'doc_name': 'materialsStore', 'get_id_by_meta': True},
                  {'db_name': 'products_store_id', 'doc_name': 'productsStore', 'get_id_by_meta': True},
                  {'db_name': 'positions', 'doc_name': 'positions'},
                  {'db_name': 'state', 'doc_name': 'state'},
                  ]
        edited = []
        for ed in edited_els:
            if ed.get('get_id_by_meta'):
                if production_task[ed['db_name']] != get_id_by_meta(args[ed['doc_name']]):
                    edited.append(ed['db_name'])
            else:
                if production_task[ed['db_name']] != args.get(ed['doc_name']):
                    edited.append(ed['db_name'])
        session.execute(sa.update(ProductionTask).where(ProductionTask.id == args['id']).values(
            applicable=args['applicable'],
            name=args['name'], description=args.get('description', ''),
            moment=args['moment'].split('.')[0],
            production_start=args.get('productionStart'),
            production_end=args.get('productionEnd'),
            delivery_planned=args.get('deliveryPlannedMoment'),
            materials_store_id=get_id_by_meta(args['materialsStore']),
            products_store_id=get_id_by_meta(args['productsStore']),
            period_delivery=period_delivery,
            positions=args['positions'],
            state=args.get('state'), edited=edited,
        ))
        return False

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(ProductionTask).where(ProductionTask.id == id))


class DBMove:

    @classmethod
    def add(cls, session: Session, args: dict):
        move = Move(
            id=args['id'], applicable=args['applicable'],
            name=args['name'], description=args.get('description', ''),
            moment=args['moment'].split('.')[0], source_store_id=get_id_by_meta(args['sourceStore']),
            target_store_id=get_id_by_meta(args['targetStore']),
            positions=args['positions'], state=args.get('state'),
            amount=args.get('sum', 0), currency_id=get_id_by_meta(args['rate']['currency']),
            edited=[],
        )
        session.add(move)

    @classmethod
    def get(cls, session: Session, id: str) -> Move:
        return session.query(Move).where(Move.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[Move]:
        return session.query(Move).all()

    @classmethod
    def get_by_start_end_date(cls, session: Session, start_date, end_date) -> list[Move]:
        return session.query(Move).where(start_date <= Move.moment).where(end_date >= Move.moment).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        move = cls.get(session, args['id'])
        if not move:
            cls.add(session, args)
            return True
        move = json.loads(str(move))
        edited_els = [{'db_name': 'applicable', 'doc_name': 'applicable'},
                      {'db_name': 'name', 'doc_name': 'name'},
                      {'db_name': 'description', 'doc_name': 'description'},
                      {'db_name': 'source_store_id', 'doc_name': 'sourceStore', 'get_id_by_meta': True},
                      {'db_name': 'target_store_id', 'doc_name': 'targetStore', 'get_id_by_meta': True},
                      {'db_name': 'positions', 'doc_name': 'positions'},
                      {'db_name': 'state', 'doc_name': 'state'},
                      {'db_name': 'amount', 'doc_name': 'sum'},
                      ]
        edited = []
        for ed in edited_els:
            if ed.get('get_id_by_meta'):
                if move[ed['db_name']] != get_id_by_meta(args[ed['doc_name']]):
                    edited.append(ed['db_name'])
            else:
                if move[ed['db_name']] != args.get(ed['doc_name']):
                    edited.append(ed['db_name'])
        session.execute(sa.update(Move).where(Move.id == args['id']).values(
            applicable=args['applicable'],
            name=args['name'], description=args.get('description', ''),
            moment=args['moment'].split('.')[0], source_store_id=get_id_by_meta(args['sourceStore']),
            target_store_id=get_id_by_meta(args['targetStore']),
            positions=args['positions'], state=args.get('state'),
            amount=args.get('sum', 0), currency_id=get_id_by_meta(args['rate']['currency']),
            edited=edited,
        ))
        return False

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(Move).where(Move.id == id))


class DBPurchaseOrder:

    @classmethod
    def add(cls, session: Session, args: dict):
        purchase_order = PurchaseOrder(
            id=args['id'], applicable=args['applicable'],
            name=args['name'], description=args.get('description', ''),
            moment=args['moment'].split('.')[0],
            delivery_planned=args.get('deliveryPlannedMoment'),
            agent_id=get_id_by_meta(args['agent']),
            target_store_id=get_id_by_meta(args['store']) if args.get('store') else None,
            positions=args['positions'],
            state=args.get('state'),
            amount=args.get('sum', 0), currency_id=get_id_by_meta(args['rate']['currency']),
        )
        session.add(purchase_order)

    @classmethod
    def get(cls, session: Session, id: str) -> PurchaseOrder:
        return session.query(PurchaseOrder).where(PurchaseOrder.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[PurchaseOrder]:
        return session.query(PurchaseOrder).all()

    @classmethod
    def get_by_start_end_date(cls, session: Session, start_date, end_date) -> list[PurchaseOrder]:
        return session.query(PurchaseOrder).where(start_date <= PurchaseOrder.delivery_planned).where(end_date >= PurchaseOrder.delivery_planned).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        purchase_order = cls.get(session, args['id'])
        if not purchase_order:
            cls.add(session, args)
            return True
        purchase_order = json.loads(str(purchase_order))
        edited_els = [{'db_name': 'applicable', 'doc_name': 'applicable'},
                      {'db_name': 'name', 'doc_name': 'name'},
                      {'db_name': 'description', 'doc_name': 'description'},
                      {'db_name': 'delivery_planned', 'doc_name': 'deliveryPlannedMoment'},
                      {'db_name': 'agent_id', 'doc_name': 'agent', 'get_id_by_meta': True},
                      {'db_name': 'target_store_id', 'doc_name': 'store', 'get_id_by_meta': True},
                      {'db_name': 'positions', 'doc_name': 'positions'},
                      {'db_name': 'state', 'doc_name': 'state'},
                      {'db_name': 'amount', 'doc_name': 'sum'},
                      ]
        edited = []
        for ed in edited_els:
            if ed.get('get_id_by_meta'):
                if purchase_order[ed['db_name']] != get_id_by_meta(args[ed['doc_name']]) if args.get(ed['doc_name']) else None:
                    edited.append(ed['db_name'])
            else:
                if purchase_order[ed['db_name']] != args.get(ed['doc_name']):
                    edited.append(ed['db_name'])
        session.execute(sa.update(PurchaseOrder).where(PurchaseOrder.id == args['id']).values(
            applicable=args['applicable'],
            name=args['name'], description=args.get('description', ''),
            moment=args['moment'].split('.')[0],
            delivery_planned=args.get('deliveryPlannedMoment'),
            agent_id=get_id_by_meta(args['agent']),
            target_store_id=get_id_by_meta(args['store']) if args.get('store') else None,
            positions=args['positions'],
            state=args.get('state'),
            amount=args.get('sum', 0), currency_id=get_id_by_meta(args['rate']['currency']),
            edited=edited,
        ))
        return False

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(PurchaseOrder).where(PurchaseOrder.id == id))


class DBSupply:

    @classmethod
    def add(cls, session: Session, args: dict):

        supply = Supply(
            id=args['id'], applicable=args['applicable'],
            name=args['name'], description=args.get('description', ''),
            moment=args['moment'].split('.')[0],
            agent_id=get_id_by_meta(args['agent']),
            target_store_id=get_id_by_meta(args['store']),
            positions=args['positions'],
            state=args.get('state'),
            amount=args.get('sum', 0), currency_id=get_id_by_meta(args['rate']['currency']),
            purchase_order_id=get_id_by_meta(args['purchaseOrder']) if args.get('purchaseOrder') else None,
            edited=[],
        )
        session.add(supply)

    @classmethod
    def get(cls, session: Session, id: str) -> Supply:
        return session.query(Supply).where(Supply.id == id).one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> list[Supply]:
        return session.query(Supply).all()

    @classmethod
    def get_by_start_end_date(cls, session: Session, start_date, end_date) -> list[Supply]:
        return session.query(Supply).where(start_date <= Supply.moment).where(end_date >= Supply.moment).all()

    @classmethod
    def add_update(cls, session: Session, args: dict):
        supply = cls.get(session, args['id'])
        if not supply:
            cls.add(session, args)
            return True
        supply = json.loads(str(supply))
        edited_els = [{'db_name': 'applicable', 'doc_name': 'applicable'},
                      {'db_name': 'name', 'doc_name': 'name'},
                      {'db_name': 'description', 'doc_name': 'description'},
                      {'db_name': 'agent_id', 'doc_name': 'agent', 'get_id_by_meta': True},
                      {'db_name': 'target_store_id', 'doc_name': 'store', 'get_id_by_meta': True},
                      {'db_name': 'positions', 'doc_name': 'positions'},
                      {'db_name': 'state', 'doc_name': 'state'},
                      {'db_name': 'amount', 'doc_name': 'sum'},
                      {'db_name': 'purchase_order_id', 'doc_name': 'purchaseOrder', 'get_id_by_meta': True},
                      ]
        edited = []
        for ed in edited_els:
            if ed.get('get_id_by_meta'):
                if supply[ed['db_name']] != get_id_by_meta(args[ed['doc_name']]) if args.get(
                        ed['doc_name']) else None:
                    edited.append(ed['db_name'])
            else:
                if supply[ed['db_name']] != args.get(ed['doc_name']):
                    edited.append(ed['db_name'])
        session.execute(sa.update(Supply).where(Supply.id == args['id']).values(
            applicable=args['applicable'],
            name=args['name'], description=args.get('description', ''),
            moment=args['moment'].split('.')[0],
            agent_id=get_id_by_meta(args['agent']),
            target_store_id=get_id_by_meta(args['store']),
            positions=args['positions'],
            state=args.get('state'),
            amount=args.get('sum', 0), currency_id=get_id_by_meta(args['rate']['currency']),
            purchase_order_id=get_id_by_meta(args['purchaseOrder']) if args.get('purchaseOrder') else None,
            edited=edited,
        ))
        return False

    @classmethod
    def remove(cls, session: Session, id):
        session.execute(sa.delete(Supply).where(Supply.id == id))