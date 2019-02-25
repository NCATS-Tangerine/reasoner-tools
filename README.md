# reasoner-tools
## renci.org

### Tools Available:

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

- TO RUN VIA PYTHON:
$PYTHONPATH=$PWD python3 greent/api/onto.py
navigate to http://localhost:5000/apidocs

- TO RUN VIA GUNICORN:
$gunicorn onto:app --workers 1 --pythonpath=$PWD/greent/api
navigate to http://127.0.0.1:8000/apidocs
make functionality changes in greent/services/ontology.py
make front-end changes in greent/api/onto.py
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

## RoboQuery v 0.1

This was paired with ROBOKOP circa August 2018. May not interact with ROBOKOP
effectively right out of the box at the present.

Framework established for a system which uses ROBOKOP Builder to instantiate a graph 
and ROBOKOP Ranker to measure properties of that graph.

In order to test out RoboQuery, you'll need ROBOKOP running locally.
Please see https://github.com/NCATS-Gamma/robokop and follow the full
instructions before proceeding with the RoboQuery instructions below.

``` To test or try-out RoboQuery:
$ python -m venv reasoner-tools_env
$ source reasoner-tools_env/bin/activate
$ git clone git@github.com:NCATS-Tangerine/reasoner-tools
$ cd reasoner-tools
$ pip install greent/roboquery_requirements.txt
$ mv shared/robokop_TEMPLATE.env shared/robokop.env
$ <editor call, e.g. vi or nano> shared/robokop.env
    --> you will need to fill in passwords for "SECRET STUFF" at the bottom,
        contact a developer if this is unclear or unknown to you.
$ source deploy/setenv.sh
$ PYTHONPATH=$PWD python builder/api/roboquery_launcher.py
```
browse to localhost:6017/apidocs