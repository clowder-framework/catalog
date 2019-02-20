from flask import g
from pymongo import MongoClient

def get_db():
    if 'db' not in g:
        client = MongoClient('mongodb://localhost:27017/')
        g.db = client
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)