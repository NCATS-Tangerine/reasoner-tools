import argparse
import glob
import json
import os
import re
import requests
import yaml
import shutil
from flask import Flask, jsonify, g, Response
from flasgger import Swagger
from lru import LRU
from greent.services.bionames import BioNames
from greent.servicecontext import ServiceContext

app = Flask(__name__)

template = {
  "swagger": "2.0",
  "info": {
    "title": "BioNames API",
    "description": "Generic facility aggregating bio-ontology lookup services to get ids based on natural language names.",
    "contact": {
      "responsibleOrganization": "renci.org",
      "responsibleDeveloper": "scox@renci.org",
      "email": "x@renci.org",
      "url": "www.renci.org",
    },
    "termsOfService": "http://renci.org/terms",
    "version": "0.0.2"
  },
  "schemes": [
    "https",
    "http"
  ]
}
app.config['SWAGGER'] = {
   'title': 'BioNames Service'
}

swagger = Swagger(app, template=template)
core = BioNames(ServiceContext.create_context ())
cache = LRU (1000)

@app.route('/lookup/<q>/<concept>/')
def lookup (q, concept):
   """ Find ids by various methods.
   ---
   parameters:
     - name: q
       in: path
       type: string
       required: true
       default: aspirin
       description: "A text string of interest. Can be a fragment."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /lookup/{{ input }}/{{ input2 }}

     - name: concept
       in: path
       type: string
       required: false
       default: drug
       description: "A biolink-model concept name, e.g. 'drug', 'disease', 'phenotypic feature', 'gene', 'cell', or 'anatomical entity'"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /is_a/{{ input }}/{{ input2 }}
   responses:
     200:
       description: ...
   """
   assert q, "A string must be entered as a query."
   assert concept, "A string must be entered as a query."
  
   # the below separation of keys ensures that a search for q = 'diabetes' returns
   # a result distinct and different if concept = 'drug' OR concept = 'disease'
   # any unique, two-term search will yield distinct results and cache them
   q_key = f"{q}"
   concept_key = f"{concept}"
   full_key = q_key + concept_key 
   if full_key in cache:
      result = cache[full_key]
   else:  
      result = core.lookup_router(q_key, concept=concept_key)
      cache[full_key] = result
   return jsonify(result)

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Rosetta Server')
   parser.add_argument('-p', '--port',  type=int, help='Port to run service on.', default=5000)
   parser.add_argument('-d', '--debug', help="Debug.", default=False)
   parser.add_argument('-c', '--conf',  help='GreenT config file to use.', default="greent.conf")
   args = parser.parse_args ()
   app.config['SWAGGER']['greent_conf'] = args.greent_conf = args.conf
   app.config['onto'] = {
       'config' : args.conf,
       'debug'  : args.debug
   }
   app.run(host='0.0.0.0', port=args.port, debug=True, threaded=True)