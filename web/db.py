import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

pwnd_username = os.environ.get('PWND_USERNAME')
pwnd_password = os.environ.get('PWND_PASSWORD')

db_username = os.environ.get('MYSQL_USER')
db_password = os.environ.get('MYSQL_PASSWORD')
db_name = os.environ.get('MYSQL_DATABASE')
db_host = 'db' # Linked with docker

URI = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(
        db_username,
        db_password,
        db_host,
        db_name,
)

engine = create_engine(URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
                                         bind=engine))

def session_commit(obj):
    session = db_session()
    session.add(obj)
    session.commit()

Base = declarative_base()
Base.query = db_session.query_property()

def clean_db():
    import models
    Base.metadata.drop_all(bind=engine)

# Utility function to init the DB
def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)
    models.User(name=pwnd_username, password=pwnd_password)
