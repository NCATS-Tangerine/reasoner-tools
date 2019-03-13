import argparse
import json
from flask import Flask, jsonify, g, Response, request
from flasgger import Swagger
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__, instance_relative_config=True)

template = {
  "swagger": "2.0",
  "info": {
    "title": "Uberongraph API Interface",
    "description": "Generic facts about ontologies.",
    "contact": {
      "responsibleOrganization": "renci.org",
      "responsibleDeveloper": "colinkcurtis@gmail.com",
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
   'title': 'UberOnto API'
}
swagger = Swagger(app, template=template)

@app.route('/id_list/<curie>')
def id_list(curie):
  """ Get a list of all available id's for a given ontology, e.g. 'MONDO' or 'HPO'.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: MONDO
       description: "The name of an ontology for which you want all id's returned, e.g. MONDO"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /id_list/{{ input }}/
   responses:
     200:
       description: ...
   """
  formatted_input = curie.replace(':','_')
  uberongraph_request_url = 'https://stars-app.renci.org/uberongraph/sparql'
  sparql = SPARQLWrapper(uberongraph_request_url)
  query_text = """
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      SELECT DISTINCT ?subject
      FROM     <http://reasoner.renci.org/ontology>
      WHERE {    
        ?subject rdfs:isDefinedBy <http://purl.obolibrary.org/obo/PLACEHOLDER.owl>
      }
      """
  formatted_query_text = query_text.replace('PLACEHOLDER', formatted_input.lower())
  sparql.setQuery(formatted_query_text)
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  #print(json.dumps(results['results'], sort_keys=True, indent = 4))
  output = []
  for item in results['results']['bindings']:
      an_id = item['subject']['value'].replace('http://purl.obolibrary.org/obo/','')
      reformatted_id = an_id.replace('_',':')
      output.append(reformatted_id)
  return jsonify(output)

@app.route('/descendants/<curie>')
def descendants(curie):
  """ Get all cascading 'is_a' descendants of an input CURIE term
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: CHEBI:23367
       description: "Get all cascading 'is_a' descendants of an input CURIE term"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /descendants/{{ input }}/
   responses:
     200:
       description: ...
   """
  formatted_input = curie.replace(':','_')
  uberongraph_request_url = 'https://stars-app.renci.org/uberongraph/sparql'
  sparql = SPARQLWrapper(uberongraph_request_url)
  query_text = """
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      SELECT DISTINCT ?term
      FROM     <http://reasoner.renci.org/ontology/closure>
      WHERE {    
        ?term rdfs:subClassOf <http://purl.obolibrary.org/obo/PLACEHOLDER>
      }
      """
  formatted_query_text = query_text.replace('PLACEHOLDER', formatted_input)
  sparql.setQuery(formatted_query_text)
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  output = []
  for term in results['results']['bindings']:
    sub_term = term['term']['value']
    output.append(sub_term)
  formatted_output = []
  for term in output:
    formatted_output.append(term.replace('http://purl.obolibrary.org/obo/','') \
    .replace('_',':').replace('http://linkedlifedata.com/resource/umls/id/','') \
    .replace('http://www.ebi.ac.uk/efo/',''))
  return jsonify(formatted_output)

@app.route('/children/<curie>')
def children(curie):
  """ Return all outgoing (once-removed subterms) via SubClassOf from the Ontology Graph
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: GO:0005576
       description: "Return all outgoing (once-removed subterms) via SubClassOf from the Ontology Graph"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /children/{{ input }}/
   responses:
     200:
       description: ...
   """
  formatted_input = curie.replace(':','_')
  uberongraph_request_url = 'https://stars-app.renci.org/uberongraph/sparql'
  sparql = SPARQLWrapper(uberongraph_request_url)
  query_text = """
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      SELECT DISTINCT ?term
      FROM     <http://reasoner.renci.org/ontology>
      WHERE {    
        ?term rdfs:subClassOf <http://purl.obolibrary.org/obo/PLACEHOLDER>
      }
      """
  formatted_query_text = query_text.replace('PLACEHOLDER', formatted_input)
  sparql.setQuery(formatted_query_text)
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  output = []
  for term in results['results']['bindings']:
    sub_term = term['term']['value']
    output.append(sub_term)
  formatted_output = []
  for term in output:
    formatted_output.append(term.replace('http://purl.obolibrary.org/obo/','') \
    .replace('_',':').replace('http://linkedlifedata.com/resource/umls/id/','') \
    .replace('http://www.ebi.ac.uk/efo/',''))
  return jsonify(formatted_output)

@app.route('/label/<curie>')
def label(curie):
  """ Get the label of a curie ID from the owl ontologies.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: MONDO:0004979
       description: "Get the label of a curie ID from the owl ontologies."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /label/{{ input }}/
   responses:
     200:
       description: ...
   """
  formatted_input = curie.replace(':','_')
  uberongraph_request_url = 'https://stars-app.renci.org/uberongraph/sparql'
  sparql = SPARQLWrapper(uberongraph_request_url)
  query_text = """
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
      SELECT DISTINCT *
      FROM     <http://reasoner.renci.org/ontology>
      WHERE {    
        <http://purl.obolibrary.org/obo/PLACEHOLDER> rdfs:label ?label
      }
      """
  formatted_query_text = query_text.replace('PLACEHOLDER', formatted_input)
  sparql.setQuery(formatted_query_text)
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  output = {}
  if results['results']['bindings']:
      label = results['results']['bindings'][0]['label']['value']
      output['id'] = curie
      output['label'] = label
  return jsonify(output)

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Rosetta Server')
   parser.add_argument('-p', '--port',  type=int, help='Port to run service on.', default=5000)
   parser.add_argument('-d', '--debug', help="Debug.", default=False)
   parser.add_argument('-t', '--data',  help="Ontology data source.", default=".")
   parser.add_argument('-c', '--conf',  help='GreenT config file to use.', default="greent.conf")
   args = parser.parse_args ()
   #app.config['SWAGGER']['greent_conf'] = args.greent_conf = args.conf
   app.config['onto'] = {
       'config' : args.conf,
       'data'   : args.data,
       'debug'  : args.debug
   }
   app.run(host='0.0.0.0', port=args.port, debug=True, threaded=True)
