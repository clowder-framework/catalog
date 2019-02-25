from flask import (
    Blueprint, render_template
)
from transformations.db import get_db

bp = Blueprint('pages', __name__)


@bp.route('/')
def home():
    db = get_db()
    collection = db["toolscatalog"]
    tools = collection.tools.find()

    return render_template('pages/home.html', tools = tools)