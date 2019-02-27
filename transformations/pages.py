from flask import (
    Blueprint, render_template, request, g, redirect, url_for
)
from transformations.db import get_db

bp = Blueprint('pages', __name__)


@bp.route('/')
def home():
    db = get_db()
    collection = db["toolscatalog"]
    transformations = collection.transformations.find()

    return render_template('pages/home.html', transformations = transformations)

@bp.route('/transformations', methods=('GET', 'POST'))
def post_transformation():
    # Check if user has logged in
    if g.user is not None:
        if request.method == 'POST':
            info_json = request.form['info_json']
            print(info_json)
        return render_template('pages/post_transformation.html')
    return redirect(url_for('auth.login'))