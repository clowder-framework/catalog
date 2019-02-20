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
export FLASK_APP=transformations/app.py
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