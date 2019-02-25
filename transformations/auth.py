
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
        ldap_client = ldap.initialize(ldap_hostname)
        ldap_client.set_option(ldap.OPT_REFERRALS, 0)
        user_dn = "uid=%s,%s,%s" % (username, current_app.config['LDAP_USER_DN'], current_app.config['LDAP_BASE_DN'])
        group_dn = "%s,%s" % (current_app.config['LDAP_GROUP_DN'], current_app.config['LDAP_BASE_DN'])
        try:
            ldap_client.protocol_version = ldap.VERSION3
            ldap_client.simple_bind_s(user_dn, password)
        except Exception as ex:
            error = ex

        try:

            search_scope = ldap.SCOPE_SUBTREE
            search_filter = "(&(objectClass=%s)(memberOf=cn=%s,%s)(uid=%s))" % (current_app.config['LDAP_OBJECTCLASS'],
                                                                                current_app.config['LDAP_GROUP'],
                                                                                group_dn, username)
            print(search_filter)
            ldap_result = ldap_client.search_s(current_app.config['LDAP_BASE_DN'], search_scope, search_filter)
            if 0 == len(ldap_result):
                error = "cannot find in this group"

        except Exception as ex:
            error = ex

        ldap_client.unbind_s()
        user = dict()
        user['id'] = username
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('pages.home'))

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
    return redirect(url_for('pages.home'))
