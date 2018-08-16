# reasoner-tools
# renci.org
# Translator Green >> Tangerine Teams


### Tools Available:

## Onto v 2

## BioNames v 2
All functions working as expected based on bionames v1 performance

## RoboQuery v 0.1

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
browse to localhost:5000/apidocs