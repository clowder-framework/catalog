import pymongo
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from transformations.db import get_db


bp = Blueprint('publish', __name__, url_prefix='/publish')
columns = ["name", "status"]


@bp.route('/approve', methods=('GET', 'POST'))
def approve():
    if request.method == 'GET':
        print("approve")
        # query mongo
        # pass json to the template
        db = get_db()
        collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
        transformations = collection.transformations.find({"status": "submitted"})
        transformations_data = []
        try:
            for data_tuple in transformations:
                data = dict()
                data['status'] = data_tuple.get('status')
                data['transformation_type'] = data_tuple.get('transformationType')
                data['name'] = data_tuple.get('transformationId')
                transformations_data.append(data)
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print(err)

        return render_template('publish/approve.html', columns=transformations_data)
    elif request.method == 'POST':
        form_dic = request.form.to_dict()
        transformation_id = form_dic.get('transformationId')
        if transformation_id:
            db = get_db()
            collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
            transformations = collection.transformations.find({"status": "submitted"})
            transformations_data = []
            for data_tuple in transformations:
                data_name = data_tuple.get('transformationId')
                if data_name == transformation_id:
                    collection.transformations.update_one({'transformationId': transformation_id},
                                                          {'$set': {'status': 'approved'}})
                else:
                    data = dict()
                    data['status'] = data_tuple.get('status')
                    data['transformation_type'] = data_tuple.get('transformationType')
                    data['name'] = data_tuple.get('transformationId')
                    transformations_data.append(data)

        print(transformation_id)
        return render_template('publish/approve.html', columns=transformations)

