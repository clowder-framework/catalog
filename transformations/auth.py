
import ldap

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        ldap_hostname = current_app.config['LDAP_HOSTNAME']
        ldap_login = ldap.initialize(ldap_hostname)
        user_dn = "uid=%s,%s,%s" % (username, current_app.config['LDAP_USER_DN'], current_app.config['LDAP_BASE_DN'])
        base_dn = "%s,%s" % (current_app.config['LDAP_GROUP_DN'], current_app.config['LDAP_BASE_DN'])
        try:
            ldap_login.protocol_version = ldap.VERSION3
            ldap_login.simple_bind_s(user_dn, password)
        except Exception as ex:
            error = ex

        ldap_login.unbind_s()
        user = dict()
        user['id'] = username
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
