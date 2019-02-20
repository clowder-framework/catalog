import os

from flask import Flask, render_template

from . import auth
from transformations.db import get_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(auth.bp)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Connect to database
    from . import db
    db.init_app(app)

    # a simple home page
    @app.route('/')
    def home():
        db = get_db()
        collection = db["toolscatalog"]
        tools = collection.tools.find()

        return render_template('home.html', tools = tools)

    return app