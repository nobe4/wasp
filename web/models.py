from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, func
from db import Base, session_commit, db_session
from uuid import uuid4
from hashlib import md5
import datetime
from datetime import timedelta

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    # MD5 hashed password
    password = Column(String(50))

    def __init__(self, name, password):
        self.name = name
        # Not hashed = bad
        self.password = md5(password.encode('utf-8')).hexdigest()

        session_commit(self)

    def __repr__(self):
        return '<User %r>' % (self.name)

    @classmethod
    def try_login(cls, name, password):
        '''Try to login with the username and password, returns two booleans:
        - Does the user exist?
        - Does the password match the user?'''
        user = cls.query.filter_by(name=name).first()

        if not user:
            return False, False

        return True, user.password == md5(password.encode('utf-8')).hexdigest()

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)

    created = Column(DateTime, default=func.now())
    flagged = Column(Boolean, default=False)
    checked = Column(Boolean, default=False)

    author = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)

    def __init__(self, content, author):
        self.content = content
        self.author = author

        session_commit(self)

    @classmethod
    def visible(cls):
        session = db_session()

        # Limit to 5 minutes display
        limit_date = datetime.datetime.now() - timedelta(seconds=60*5)

        posts = session.query(cls) \
                .filter(Post.flagged==False) \
                .filter(Post.created>limit_date) \
                .all()
        session.commit()
        return posts

    @classmethod
    def post_to_check(cls):
        session = db_session()
        posts = session.query(Post).filter_by(flagged=True, checked=False).all()
        session.commit()

        if posts:
            return posts[-1].id

        return -1

    def author_name(self):
        return User.query.get(self.author).name

    def __repr__(self):
        return '<Post by {}: {}>'.format(self.author_name(), self.content[0:10])
