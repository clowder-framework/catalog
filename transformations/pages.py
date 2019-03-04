from flask import (
    Blueprint, render_template, request, g, redirect, url_for, current_app
)
from transformations.db import get_db
import gridfs
import codecs
import json
import datetime

bp = Blueprint('pages', __name__)

def getIcon(tool_names):
    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
    tool = collection.tools.find_one({"title": tool_names})
    image = ""
    gridFSIcon = gridfs.GridFS(collection, "icons")
    fs = gridFSIcon.find_one({"metadata.tool_id": str(tool["_id"])})
    if fs:
        base64_data = codecs.encode(fs.read(), 'base64')
        image = base64_data.decode('utf-8')
    return image

@bp.route('/')
def home():
    # example: /?software=Cell+Profiler
    software = request.args.get('software')
    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
    if software:
        transformations = collection.transformations.find({"dependencies": software})
    else:
        transformations = collection.transformations.find()
    return render_template('pages/home.html', transformations = transformations, getIcon = getIcon)


@bp.route('/softwares')
def softwares():

    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]

    tools = collection.tools.find()
    return render_template('pages/softwares.html', tools = tools, getIcon = getIcon)


@bp.route('/transformations', methods=('GET', 'POST'))
def post_transformation():
    # Check if user has logged in
    if g.user is not None:
        if request.method == 'POST':
            info_json = request.form['info_json']
            transformation_type = request.form['radioOptions']

            try:
                dict_info_json = json.loads(info_json)

                db = get_db()
                database = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]

                source_code_url = None
                docker_image_name = None

                for repo in dict_info_json["repository"]:
                    if repo["repType"] == "git":
                        source_code_url = repo["repUrl"]
                    if repo["repType"] == "docker":
                        docker_image_name = repo["repUrl"]

                dict_info_json["transformationId"] = dict_info_json.pop("name")
                dict_info_json["externalServices"] = dict_info_json.pop("external_services")
                dict_info_json["url"] = source_code_url
                dict_info_json["dockerImageName"] = docker_image_name
                dict_info_json["transformationType"] = transformation_type
                dict_info_json["status"] = "submitted"
                dict_info_json.pop("repository")
                dict_info_json["created"] = datetime.datetime.utcnow()
                dict_info_json["updated"] = datetime.datetime.utcnow()

                print(dict_info_json)
                result_id = database.transformations.insert(dict_info_json)
                print(transformation_type + " added. ID: "  + result_id)

            except ValueError as e:
                print("Invalid JSON.")
                raise

        return render_template('pages/post_transformation.html')
    return redirect(url_for('auth.login'))


