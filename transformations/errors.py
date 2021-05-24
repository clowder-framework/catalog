from flask import Blueprint, render_template, app, flash

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(Exception)
def handle_all_errors(e):
    flash(e)
    return render_template('pages/home.html', err=e)

