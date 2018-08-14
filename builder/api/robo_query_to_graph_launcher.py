import argparse
import json
import os
import requests
from flask import Flask, jsonify, g, Response
from flasgger import Swagger
from lru import LRU
from greent.services.robo_query_to_graph import RoboQueryToGraph
from greent.servicecontext import ServiceContext

app = Flask(__name__)

template = {
  "swagger": "2.0",
  "info": {
    "title": "ROBOKOP Graph Query API",
    "description": "Generic API to turn small queries into large, enriched knowledge graphs.",
    "contact": {
      "responsibleOrganization": "renci.org",
      "responsibleDeveloper": "ckcurtis@renci.org",
      "email": "x@renci.org",
      "url": "www.renci.org",
    },
    "termsOfService": "http://renci.org/terms",
    "version": "0.0.1"
  },
  "schemes": [
    "https",
    "http"
  ]
}
app.config['SWAGGER'] = {
   'title': 'ROBOKOP Query to Graph Service'
}

swagger = Swagger(app, template=template)
#core = RoboQueryToGraph(ServiceContext.create_context ())
#cache = LRU (1000)

@app.route('/api/querytograph')
def query_to_graph_utility (curie = "MONDO:0005737", test="TEST"):
   """ Find ids by various methods.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: false
       default: MONDO:0005737
       description: "Enter an ontological ID."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /is_a/{{ input }}/{{ input2 }}
     
     - name: test
       in: path
       type: string
       required: false
       default:
       description: "corresponding to the ID above"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /is_a/{{ input }}/{{ input2 }}
     
   responses:
     200:
       description: ...
   """

   # We need to take the above "STUFF" and make it fit into:
   # 
   builder_query_1_url = "http://127.0.0.1:6010/api/"
   builder_query_1_headers = {
     'accept' : 'application/json',
     'Content-Type' : 'application/json' 
   }
  #  builder_query_1_data = {
  #    "machine_question": { "edges": [{"source_id": 0, "target_id": 1}, {"source_id": 1, "target_id": 2}], "nodes": [{"curie": "MONDO:0005737", "id": 0, "name": "Ebola hemorrhagic fever", "type": "disease"}, {"id": 1, "type": "gene" }, {"id": 2,  "type": "genetic_condition"}]}
  #  }

   builder_query_1_data_1 = {
            "machine_question": {
              "edges": [
                {
                  "source_id": 0,
                  "target_id": 1
                },
                {
                  "source_id": 1,
                  "target_id": 2
                }
              ],
              "nodes": [
                {
                  "curie": "MONDO:0005737",
                  "id": 0,
                  "name": "Ebola hemorrhagic fever",
                  "type": "disease"
                },
                {
                  "id": 1,
                  "type": "gene"
                },
                {
                  "id": 2,
                  "type": "genetic_condition"
                }
              ]
            }
          }

   builder_query_1_data_2 = '{  \\"machine_question\\": {    \\"edges\\": [      {        \\"source_id\\": 0,        \\"target_id\\": 1      },      {        \\"source_id\\": 1,        \\"target_id\\": 2      }    ],    \\"nodes\\": [      {        \\"curie\\": \\"MONDO:0005737\\",        \\"id\\": 0,        \\"name\\": \\"Ebola hemorrhagic fever\\",        \\"type\\": \\"disease\\"      },      {        \\"id\\": 1,        \\"type\\": \\"gene\\"      },      {        \\"id\\": 2,        \\"type\\": \\"genetic_condition\\"      }    ]  }}'

   builder_query_1_data_3 = '{  "machine_question": {    "edges": [      {        "source_id": 0,        "target_id": 1      },      {        "source_id": 1,        "target_id": 2      }    ],    "nodes": [      {        "curie": "MONDO:0005737",        "id": 0,        "name": "Ebola hemorrhagic fever",        "type": "disease"      },      {        "id": 1,        "type": "gene"      },      {        "id": 2,        "type": "genetic_condition"      }    ]  }}'


   builder_query_1_response = requests.post(builder_query_1_url, headers = builder_query_1_headers, json = builder_query_1_data_1)
  
   print(builder_query_1_response.status_code)
   print(builder_query_1_response.encoding)
   print(builder_query_1_response.text)

   return ('testing.. aug 14 2018')

#assert curie, "A string must be entered as a query."
   #assert name, "A string must be entered as a query."
  
   # the below separation of keys ensures that a search for q = 'diabetes' returns
   # a result distinct and different if concept = 'drug' OR concept = 'disease'
   # any unique, two-term search will yield distinct results and cache them
  #  curie_key = f"{curie}"
  #  name_key = f"{name}"
  #  full_key = curie_key + name_key 
  #  if full_key in cache:
  #     result = cache[full_key]
  #  else:  
  #     result = core.lookup_router(curie_key, name=name_key)
  #     cache[full_key] = result
  #  return jsonify(result)

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Robo_query_to_graph Server')
   parser.add_argument('-p', '--port',  type=int, help='Port to run service on.', default=5000)
   parser.add_argument('-d', '--debug', help="Debug.", default=False)
   parser.add_argument('-c', '--conf',  help='GreenT config file to use.', default="greent.conf")
   args = parser.parse_args ()
   app.config['SWAGGER']['greent_conf'] = args.greent_conf = args.conf
   app.config['robo_query_to_graph'] = {
       'config' : args.conf,
       'debug'  : args.debug
   }
   app.run(host='0.0.0.0', port=args.port, debug=True, threaded=True)