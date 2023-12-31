import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base

# db_auth = {
#     'user': 'postgres',
#     'password': 'admin',
#     'host': 'localhost',
#     'port': 5432,
#     'db_name': 'calendar_postavka'
# }


#url = f'postgresql+psycopg2://{db_auth["user"]}:{db_auth["password"]}@{db_auth["host"]}/{db_auth["db_name"]}'
DATABASE_URL = os.environ.get("DATABASE_URL")
log = logging.getLogger('sqlalchemy.engine.Engine')
log.setLevel('ERROR')
db_handler = logging.FileHandler('log.log')
log.propagate = False
log.addHandler(db_handler)
engine = create_engine(DATABASE_URL, max_overflow=-1)
Session = sessionmaker(engine, autoflush=True, expire_on_commit=False)
Base.metadata.create_all(engine)
