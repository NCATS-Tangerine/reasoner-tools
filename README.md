# reasoner-tools
# a brief history of work

## July 23, 2018

# Onto v2

# BioNames v2
All functions working as expected based on bionames v1 performance

## August 14, 2018

# RoboQuery v1

Framework established for a system which uses ROBOKOP Builder to instantiate a graph 
and which then uses ROBOKOP Ranker to measure portions of that graph.

Three steps are viable... 

``` To test or try-out RoboQuery v1
$ python -m venv reasoner-tools_env
$ source reasoner-tools_env/bin/activate
$ git clone git@github.com:NCATS-Tangerine/reasoner-tools
$ cd reasoner-tools
$ pip install robo_query_to_graph_requirements.txt
$ PYTHONPATH=$PWD python builder/api/robo_query_to_graph_launcher.py

then see localhost:5000/apidocs
```
