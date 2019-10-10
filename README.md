# reasoner-tools
## renci.org

### Tools Available:

## Onto API
### To edit/execute/test Onto API locally:

```
- TO EDIT:
$git clone git@github.com:NCATS-Translator/reasoner-tools

- make a virtual env and activate it, recommended as follows:
$python3 -m venv YOUR_ENV_NAME
$source YOUR_ENV_NAME/bin/activate

$cd reasoner-tools

Make functionality changes in greent/services/ontology.py
Make front-end changes in greent/api/onto_gunicorn.py
The above two files should be considered in tandem.

Add unit test cases to greent/test/test_ontology.py


- TO RUN:
$pip install -r greent/requirements.txt
$export greent_conf=greent/greent.conf

$gunicorn onto_gunicorn:app --workers 1 --pythonpath=$PWD/greent/api
Navigate in your browser to http://127.0.0.1:8000/apidocs.


- TO TEST:
$cd reasoner-tools
    
- To run all unit tests:
pytest greent/test/test_ontology.py
    
- Remove warnings and get more information as tests run:
pytest -p no:warnings -vv greent/test/test_ontology.py
    
- Run a single unit test:
pytest greent/test/test_ontology.py -k <test_name>
pytest greent/test/test_ontology.py -k test_label
```

## BioNames API
### To edit/execute/test BioNames API locally:

```
- TO EDIT:
$git clone git@github.com:NCATS-Translator/reasoner-tools

- make a virtual env and activate it, recommended as follows:
$python3 -m venv YOUR_ENV_NAME
$source YOUR_ENV_NAME/bin/activate

$cd reasoner-tools

Make functionality changes in greent/services/bionames.py
Make front-end changes in builder/api/naming.py
The above two files should be considered in tandem.

Add unit test cases to greent/test/test_bionames.py


- TO RUN:
$pip install -r greent/requirements.txt

$PYTHONPATH=$PWD python3 builder/api/naming.py
- Navigate in your browser to localhost:5000/apidocs.


- TO TEST:
$cd reasoner-tools
    
- To run all unit tests:
pytest greent/test/test_bionames.py
    
- Remove warnings and get more information as tests run:
pytest -p no:warnings -vv greent/test/test_bionames.py
    
- Run a single unit test:
pytest greent/test/test_bionames.py -k <test_name>
pytest greent/test/test_bionames.py -k test_lookup_router
```
