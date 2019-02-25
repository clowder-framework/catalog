
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = dict()
        user['id'] = "demo"
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))

        flash(error)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_id


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
