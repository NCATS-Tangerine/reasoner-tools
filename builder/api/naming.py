import argparse
import glob
import json
import os
import re
from flask import Flask, jsonify, g, Response, request
from flasgger import Swagger
from lru import LRU
from greent.services.bionames import BioNames
from greent.servicecontext import ServiceContext

app = Flask(__name__)

template = {
  "swagger": "2.0",
  "info": {
    "title": "BioNames API",
    "description": "Bionames is a generic facility which aggregates bio-ontology lookup services to retrieve names from IDs or IDs based on Natural Language names.",
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
       default: asthma
       description: "A text string of interest. If 'include_similar' is set to true, fragments may be used. 'include_similar' also makes the search NOT case sensitive. "
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /lookup/{{ input }}/{{ input2 }}

     - name: concept
       in: path
       type: string
       required: false
       default: disease
       description: "A biolink-model concept name, e.g. 'drug', 'disease', 'phenotypic feature', 'gene', 'cell', or 'anatomical entity'"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /is_a/{{ input }}/{{ input2 }}

     - name: include_similar
       in: query
       type: boolean
       default: true
       x-valueType:
         - http://schema.org/boolean
       x-requestTemplate:
         - valueType: http://schema.org/boolean
   responses:
     200:
       description: ...
   """
   assert q, "A string must be entered as a query."
   assert concept, "A string must be entered as a query."
   include_similar = request.args.get('include_similar')
   q_key = f"{q}"
   concept_key = f"{concept}"
   include_similar_key = f"{include_similar}"
   full_key = q_key + concept_key + include_similar_key
   if full_key in cache:
      result = cache[full_key]
   else:  
      result = core.lookup_router(q_key, concept=concept_key)
      if include_similar_key == 'false':
        result = [x for x in result if x['label'] == q_key]
      cache[full_key] = result
   return jsonify(result)

@app.route('/ID_to_label/<ID>/')
def ID_to_label (ID):
   """ Find Natural Language labels based on an input ID.
   ---
   parameters:
     - name: ID
       in: path
       type: string
       required: true
       default: MONDO:0004634
       description: "An ID (CURIE) of interest, e.g. GO:2001317 or MESH:D001241"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /ID_to_label/{{ input }}

   responses:
     200:
       description: ...
   """  
   ID_key = f"{ID}"
   if ID_key in cache:
     result = cache[ID_key]
   else:
     result = core.ID_to_label_lookup(ID=ID_key)
     cache[ID_key] = result
   return jsonify(result)

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='BioNames Server')
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
