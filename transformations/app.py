from flask import render_template, Blueprint, request
from flask import Flask

app = Flask(__name__)
#     # app.config.from_object(config[config_filename])
#     configure_views(app)
#     return app

@app.route('/')
def home():
    return render_template('home.html')

#
# @blueprint.route('/about')
# def about():
#     return render_template('pages/about.html')


# def create_app(config_filename):
#     app = Flask(__name__)
#     # app.config.from_object(config[config_filename])
#     configure_views(app)
#     return app