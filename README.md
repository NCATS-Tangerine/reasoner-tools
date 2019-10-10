# reasoner-tools
## renci.org

### Tools Available:

## UberOnto API
### version h-bar/2

```
updates to follow
```

## Onto API
### To edit/execute Onto API locally:

```
$git clone git@github.com:NCATS-Translator/reasoner-tools

- make a virtual env and activate it, recommended as follows:
$python3 -m venv YOUR_ENV_NAME
$source YOUR_ENV_NAME/bin/activate

$cd reasoner-tools

$pip install -r greent/requirements.txt
$export greent_conf=greent/greent.conf

- TO RUN:
$gunicorn onto_gunicorn:app --workers 1 --pythonpath=$PWD/greent/api
navigate to http://127.0.0.1:8000/apidocs

make functionality changes in greent/services/ontology.py
make front-end changes in greent/api/onto_unicorn.py
the above two files should be considered in tandem
```

## BioNames API

```
$git clone git@github.com:NCATS-Translator/reasoner-tools

- make a virtual env and activate it, recommended as follows:
$python3 -m venv YOUR_ENV_NAME
$source YOUR_ENV_NAME/bin/activate

$cd reasoner-tools

$pip install -r greent/requirements.txt

- TO RUN VIA PYTHON:
$PYTHONPATH=$PWD python3 builder/api/naming.py
-navigate to localhost:5000/apidocs

make functionality changes in greent/services/bionames.py
make front-end changes in builder/api/naming.py
the above two files should be considered in tandem
```
