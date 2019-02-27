from flask import (
    Blueprint, render_template, request, g, redirect, url_for, current_app
)
from transformations.db import get_db
import gridfs
import codecs

bp = Blueprint('pages', __name__)


@bp.route('/')
def home():
    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
    transformations = collection.transformations.find()
    # transformations = collection.transformations.find_and_modify(query={},update={"$set": {'icon': "Mike2"}})
    gridFSIcon = gridfs.GridFS(collection, "icons")
    # print(transformations.__class__)
    def getIcon(tool_names):
        tool = collection.tools.find_one({"title": tool_names[0]})
        print(str(tool["_id"]))
        image = ""

        fs = gridFSIcon.find_one({"metadata.tool_id": str(tool["_id"])})
        if fs:
            base64_data = codecs.encode( fs.read(), 'base64')
            image = base64_data.decode('utf-8')
        return image

    return render_template('pages/home.html', transformations = transformations, getIcon = getIcon)

@bp.route('/transformations', methods=('GET', 'POST'))
def post_transformation():
    # Check if user has logged in
    if g.user is not None:
        if request.method == 'POST':
            info_json = request.form['info_json']
            print(info_json)
        return render_template('pages/post_transformation.html')
    return redirect(url_for('auth.login'))


