import os

from flask import Flask, render_template, current_app

import logging
import json
from . import auth
from . import publish
from . import pages
from . import api
from transformations.db import get_db


def create_app(test_config=None):
    logging.basicConfig(format='%(asctime)-15s [%(threadName)-15s] %(levelname)-7s :' ' %(name)s - %(message)s', level=logging.INFO)
    if test_config is None:
        try:
            with open('instance/config.json') as json_file:
                config = json.load(json_file)
        except IOError as e:
            # If the file is unreadable for any reason, make sure the config is set to None
            config = None
    else:
        config = test_config

    if config is not None and 'URL_PREFIX' in config:
        prefix = config['URL_PREFIX']
        staticpath = prefix+'/static'
    else:
        prefix = None
        staticpath = '/static'

    app = Flask(__name__, instance_relative_config=True, static_url_path=staticpath)
    if config is None:
        # load the instance config, if it exists, when a configuration is not already in existence
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the prior config if already loaded
        app.config.from_mapping(config)

    # create and configure the app
    app.register_blueprint(auth.bp, url_prefix=prefix+'/auth', static_folder="static")
    app.register_blueprint(publish.bp, url_prefix=prefix+'/publish', static_folder="static")
    app.register_blueprint(pages.bp, url_prefix=prefix, static_folder="static")
    app.register_blueprint(api.bp, url_prefix=prefix+'/api/v2', static_folder="static")
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
