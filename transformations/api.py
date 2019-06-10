from flask import (
    Blueprint, current_app
)
from transformations.db import get_db
import json
from bson import ObjectId, json_util

bp = Blueprint('api', __name__, url_prefix='/api/v2')
toolTypes = {
    "converter": 1,
    "extractor": 2,
}

def jsonList(type):
    db = get_db()
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
    retVal = []
    for toolInfo in collection.tools.find({"tooltype": type}):
        retVal.append(singleToolInfo(str(ObjectId(toolInfo['_id'])), db))
    return json.dumps(retVal, default = json_util.default)  # Not sure this is json formatted

def singleToolInfo(id, db):
    # I am overloading id to work with either the toolVersionId, or if that isn't found
    #   then looking at the toolId, this is a functional change from v1
    # Other differences from v1:
    #   creationDate and updateDate are formatted differently (should be updated)
    #   params hash does not exist containing dockerfile, sampleInput, sampleOutput, extractorName, dockerimageName
    #     these are instead in the top level of the toolVersion
    #     extractorDef, and queueName are no longer in the database
    #   There are additional entries: deployments, created, and updated times in tool table
    #   reviews are no longer in the database
    #   tool_id exists in toolVersion table, changing from toolId. I have included toolId as an additional entry in the output
    collection = db[current_app.config['TRANSFORMATIONS_DATABASE_NAME']]
    versionInfo = collection.tool_versions.find_one({"_id": ObjectId(id)})
    if versionInfo is None:
        versionInfo = collection.tool_versions.find_one({"tool_id": id})
    if versionInfo is not None:
        toolId = versionInfo['tool_id']
        toolInfo = collection.tools.find_one({"_id": ObjectId(toolId)})
        toolVerId = str(ObjectId(versionInfo['_id']))
        del versionInfo["_id"]
        del toolInfo["_id"]
        versionInfo['toolVersionId'] = toolVerId
        versionInfo['toolId'] = toolId
        toolInfo['toolId'] = toolId
        for tooltype, value in toolTypes.items():
            if toolInfo['tooltype'] == value:
                toolInfo['tooltype'] = tooltype
                break
        retVal = {'tool': toolInfo, 'toolVersion': versionInfo}
    else:
        retVal = None
    return retVal

@bp.route('converters')
def convertersList():
    return jsonList(toolTypes['converter'])

@bp.route('extractors')
def extractorsList():
    return jsonList(toolTypes['extractor'])