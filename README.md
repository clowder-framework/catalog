# BD Transformations Catalog


## Getting Started

### 1. Clone Repository
```
https://opensource.ncsa.illinois.edu/bitbucket/scm/bd/bd-transformations-catalog.git
```

### 2. Setup Environment
```
cd bd-trasformations-catalog
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run in Development Mode

```
export FLASK_APP=transformations
export FLASK_ENV=development
flask run
```

## PyMongo Code Snippet

```
from pymongo import MongoClient

# Create client
client = MongoClient('mongodb://localhost:27017/')

# Connecting to database
db = client['test-database']

# Getting collection
collection = db['test-collection']

```

## Database Code Snippets

1. From Tools Catalog to Transformations Collection
```
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
```
2. Update Transformations Collection

```
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

```

3. Create index for search

```
db.getCollection('transformations').createIndex( { transformationId: "text", description: "text" } )
```

## Configuration File

1. File Basics

Each line of the configuration file should contain one configuration setting and its value. Use an equal sign (=) between the setting and the value, and put quotes (") around the value. Comments can be made by adding a pound sign (#) before what you want to comment out.

2. Available Configuration Settings

TRANSFORMATIONS_DATABASE_URI: The URI for the Mongo database. Use the Connection String URI format as described at https://docs.mongodb.com/manual/reference/connection-string/.
TRANSFORMATIONS_DATABASE_NAME: The name of the Mongo database.
LDAP_HOSTNAME: The full URI to the LDAP server. Include the port if non-standard.
LDAP_GROUP: The LDAP group name that contains people that are authorized.
LDAP_BASE_DN: The base DN for the LDAP server.
LDAP_USER_DN: Applied to the base DN to find users.
LDAP_GROUP_DN: Applied to the base DN to find groups.
LDAP_OBJECTCLASS: An LDAP object class that applies to users.
LDAP_TRUST_ALL_CERTIFICATES: A True/False setting.
ADMINS: A list of users in LDAP that have administrator permissions to the catalog.
URL_PREFIX: This can be used if you need to prefix all URLs with a prefix. Then you can set up a proxy to forward to the given server with this prefix and have the routes work with the prefix.

## Docker

1. Build image

The image is based on python:3 to have gcc installed initially. python-ladp library still requires OS libraries, which are described in Dockerfile.

You can build your docker image with the command:
```bash
% docker build -t transformation .
```

2. Run docker image

Use the instance/config.py.template as template to create config.py.

For macOS, you can set url in TRANSFORMATIONS_DATABASE_URI as 'docker.for.mac.host.internal'. Note the host name maybe changed according to your docker version.
Refer to : https://stackoverflow.com/questions/31249112/allow-docker-container-to-connect-to-a-local-host-postgres-database

To run the docker image you may like the following command line:
```bash
% docker run --rm -d -p 5000:5000 -v path_to_conf/config.py:/app/instance/config.py transformation
```

