from flask import Blueprint, render_template, app

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(Exception)
def handle_all_errors(e):
    return render_template('pages/error.html', err=e)

