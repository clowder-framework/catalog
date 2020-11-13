from bson import ObjectId
from flask import (
    Blueprint, render_template, request, g, redirect, url_for, current_app
)
from transformations.db import get_db
import gridfs
import codecs
import json
import datetime
from werkzeug.exceptions import HTTPException
from pymongo.collation import Collation


bp = Blueprint('pages', __name__)

def getIcon(tool_name):
    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
    tool = collection.tools.find_one({"title": tool_name})
    image = ""
    if (tool):
        gridFSIcon = gridfs.GridFS(collection, "icons")
        fs = gridFSIcon.find_one({"metadata.tool_id": str(tool["_id"])})
        if fs:
            base64_data = codecs.encode(fs.read(), 'base64')
            image = base64_data.decode('utf-8')
    return image

def hasIcons(softwares):
    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
    for tool_name in softwares:
        tool = collection.tools.find_one({"title": tool_name})
        if (tool):
            gridFSIcon = gridfs.GridFS(collection, "icons")
            fs = gridFSIcon.find_one({"metadata.tool_id": str(tool["_id"])})
            if fs:
                return True
    return False

def replaceEmptyString(text):
    return text if text else "None"

@bp.route('/')
def home():
    # example: /?software=Cell+Profiler
    software = request.args.get('software')
    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
    if software:
        transformations = collection.transformations.find({"dependencies": software})
    else:
        transformations = collection.transformations.find({"status": "approved"})
    return render_template('pages/home.html', transformations = transformations, getIcon = getIcon,
                           hasIcons = hasIcons)


@bp.route('/softwares')
def softwares():

    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]

    tools = collection.tools.find()
    raise HTTPException()
    return render_template('pages/softwares.html', tools = tools, getIcon = getIcon)


@bp.route('/transformations', methods=('GET', 'POST'))
def post_transformation():
    # Check if user has logged in or anonymous submission is allowed
    if g.user is not None or current_app.config["ANONYMOUS_SUBMISSION"].lower() == "true":
        if request.method == 'POST':

            transformation_type = request.form['radioOptions']

            try:
                if request.form['create'] == "json":
                    info_json = request.form['info_json']
                    dict_info_json = json.loads(info_json)
                    source_code_url = None
                    docker_image_name = None
                    for repo in dict_info_json["repository"]:
                        if repo["repType"] == "git":
                            source_code_url = repo["repUrl"]
                        if repo["repType"] == "docker":
                            docker_image_name = repo["repUrl"]
                    dict_info_json["url"] = source_code_url
                    dict_info_json["dockerImageName"] = docker_image_name
                    dict_info_json.pop("repository")
                    dict_info_json.pop("@context")
                else:
                    dict_info_json = request.form.to_dict(flat=False)
                    single_fields = ["name", "version", "author", "description", "dockerImageName", "url"]
                    for f in single_fields:
                        dict_info_json[f]= dict_info_json[f][0]
                    if transformation_type == "extractor":

                        dict_info_json["contexts"][0] = json.loads(dict_info_json["contexts"][0])
                        dict_info_json["process"] = json.loads(dict_info_json["process"])
                    else:
                        dict_info_json["input_formats"] = dict_info_json["input_formats"][0].replace(" ", "").split(",")
                        dict_info_json["output_formats"] = dict_info_json["output_formats"][0].replace(" ", "").split(",")

                db = get_db()
                database = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]

                dict_info_json["transformationId"] = dict_info_json.pop("name")
                dict_info_json["externalServices"] = dict_info_json.pop("external_services")

                dict_info_json["transformationType"] = transformation_type
                dict_info_json["status"] = "submitted"

                dict_info_json["created"] = datetime.datetime.utcnow()
                dict_info_json["updated"] = datetime.datetime.utcnow()

                print(dict_info_json)
                # Prior to insert, check the name and version if they already exist then error out, otherwise insert
                query_result_id = database.transformations.find_one({
                    "transformationId": dict_info_json["transformationId"], "version": dict_info_json["version"]})
                if query_result_id:
                    return redirect(url_for('pages.update_transformation', transformation_id = query_result_id["_id"]))
                result_id = database.transformations.insert(dict_info_json)
                print(transformation_type + " added. ID: "  + str(result_id))
                return redirect(url_for('pages.view_transformation', transformation_id = result_id))
            except ValueError as e:
                raise ValueError("Invalid JSON.")
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError("Unable to decode the JSON")
            except KeyError as ke:
                raise KeyError("There is a missing necessary section of the extractor info")


        return render_template('pages/post_transformation.html')
    return redirect(url_for('auth.login'))

@bp.route('/transformations/form', methods=['GET'])
def transformation_form():
    if g.user is not None:
        db = get_db()
        collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]

        tools = collection.tools.find({}, {"title":1})
        return render_template('pages/post_transformation_form.html', tools = tools)
    return redirect(url_for('auth.login'))

@bp.route('/transformations/<transformation_id>', methods=['GET'])
def view_transformation(transformation_id):
    try:

        db = get_db()
        database = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
        transformation  = database.transformations.find_one({ "_id": ObjectId(transformation_id)})
        alltransformations = database.transformations.find({"transformationId":
                                                             transformation["transformationId"] }).sort("version", -1).\
                                                             collation(Collation(locale='en_US', numericOrdering=True))

    except Exception as e:
        print("Exception")
        raise
    return render_template('pages/view_transformation.html', originalTransformation = transformation,
                           transformations = alltransformations, getIcon = getIcon,
                           replaceEmptyString = replaceEmptyString)

@bp.route('/search', methods=['GET'])
def search():
    try:
        db = get_db()
        database = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
        # text search for transformationId & description
        transformation  =  database.transformations.find({ "$text": { "$search": request.args.get("search")}} )

    except Exception as e:
        print("Exception")
        raise
    return render_template('pages/home.html', transformations = transformation, getIcon = getIcon,
                           hasIcons = hasIcons)

@bp.route('/transformations/<transformation_id>/update', methods=['GET', 'POST'])
def update_transformation(transformation_id):
    return "A transformation already exists with that name and version.", 501
