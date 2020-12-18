from pymongo import MongoClient

# Create client
client = MongoClient('mongodb://localhost:27017/')

# Connecting to database
db = client['tools_catalog']

# Getting collection
collection = db['tools_version']

db.tool_versions.find().forEach(
    function(toolv) {
        toolv.dependencies = db.tools.find({
            "_id": ObjectId(toolv.tool_id)
        }).map(function(doc) {
            return doc.title
        });
        toolv.transformation_type = db.tools.find({
            "_id": ObjectId(toolv.tool_id)
        }).map(function(doc) {
            if (doc.tooltype == 1) {
                return "converter"
            } else {
                return "extractor"
            }
        })[0]


        toolv.transformation_id = toolv.extractor_name;
        toolv.title = toolv.version
        db.transformations.insert(toolv);
    }
);

db.transformations.update({}, {
        $unset: {
            'extractor_name': 1,
            "tool_id": 1,
            "version": 1
        }
    },
    false, true
)

db.transformations_new.drop();

db.transformations.find().forEach(
    function (transformation) {
    	var newTransformation = {};

    	newTransformation["dateCreated"] = transformation["creationDate"];
    	newTransformation["dateUpdated"] = transformation["updateDate"];
    	newTransformation["description"] = transformation["whatsnew"];
    	newTransformation["url"] = transformation["url"];
    	newTransformation["dockerImageName"] = transformation["dockerimageName"];
    	newTransformation["author"] = transformation["author"];
    	newTransformation["dependencies"] = transformation["dependencies"];
    	newTransformation["externalServices"] = [];
    	newTransformation["transformationType"] = transformation["transformation_type"];
    	newTransformation["transformationId"] = transformation["transformation_id"];
    	newTransformation["transformationId"] = transformation["transformation_id"];
    	newTransformation["title"] = transformation["title"];
    	newTransformation["status"] = "submitted";

    	db.transformations_new.insert(newTransformation);
    }
);

db.transformations.renameCollection("transformations_backup");
db.transformations_new.renameCollection("transformations");

db.transformations.updateMany( {}, { $rename: { "dateCreated": "created", "dateUpdated": "updated" } } );
db.icons.files.updateMany( {}, { $rename: { "uploadDate": "uploaded" } } );
db.tools.updateMany( {}, { $rename: { "creationDate": "created", "updateDate": "updated" } } );
