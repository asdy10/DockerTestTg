import json

from db.db_connect import Session
from db.queries import DBProduct, DBVariant


class DBBuffer:

    def __init__(self):
        self.products = {}
        self.variants = {}
        self.update_from_db()

    def get_product(self, id):
        return self.products.get(id)

    def get_variant(self, id):
        return self.variants.get(id)

    def update_from_db(self):
        with Session.begin() as session:
            self.products = DBProduct.get_all(session)
            self.products = json.loads(str(self.products))
            self.products = {i['id']: i for i in self.products}
            self.variants = DBVariant.get_all(session)
            self.variants = json.loads(str(self.variants))
            self.variants = {i['id']: i for i in self.variants}


db_buffer = DBBuffer()
