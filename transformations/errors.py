from flask import render_template, app
import transformations
from transformations import api
from transformations import auth
from transformations import db
from transformations import pages
from transformations import publish

@transformations.errorhandler(Exception)
def handle_all_errors(e):
    return render_template('pages/error.html', error=e)

#@auth.errorhandler(Exception)
#def handle_all_errors(e):
#    return render_template('pages/error.html', error=e)

#@db.errorhandler(Exception)
#def handle_all_errors(e):
#    return render_template('pages/error.html', error=e)

#@pages.errorhandler(Exception)
#def handle_all_errors(e):
#    return render_template('pages/error.html', error=e)

#@publish.errorhandler(Exception)
#def handle_all_errors(e):
#    return render_template('pages/error.html', error=e)
