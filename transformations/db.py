from flask import current_app, g
from pymongo import MongoClient

def get_db():
    if 'db' not in g:
        client = MongoClient(current_app.config['TRANSFORMATIONS_DATABASE_URI'])
        g.db = client
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)