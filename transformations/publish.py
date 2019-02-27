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
        transformations = collection.transformations.find({"submitted": True})
        transformations_data = []
        try:
            for data_tuple in transformations:
                data = dict()
                data['status'] = data_tuple.get('status')
                data['transformation_type'] = data_tuple.get('transformation_type')
                data['name'] = data_tuple.get('transformation_id')
                transformations_data.append(data)
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print(err)

        return render_template('publish/approve.html', columns=transformations_data)
    elif request.method == 'POST':
        form_dic = request.form.to_dict()
        # TODO: remove submitted true from document and insert approved: true into document
        transformations = [{"name": "extractor1", "status": 4}, {"name": "extractor2", "status": 5}]

        transformation_id = form_dic.get('transformationId')
        print(transformation_id)
        return render_template('publish/approve.html', columns=transformations)

