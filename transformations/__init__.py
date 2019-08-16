import os

from flask import Flask, render_template, current_app

from . import auth
from . import publish
from . import pages
from . import api
from werkzeug import DispatcherMiddleware
from transformations.db import get_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    if app.config['URL_PREFIX'] is not None:
        app.config['STATIC_FOLDER'] = app.config['URL_PREFIX']
        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {app.config['URL_PREFIX']: app.wsgi_app})
    # create and configure the app
    app.register_blueprint(auth.bp)
    app.register_blueprint(publish.bp)
    app.register_blueprint(pages.bp)
    app.register_blueprint(api.bp)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Connect to database
    from . import db
    db.init_app(app)

    return app