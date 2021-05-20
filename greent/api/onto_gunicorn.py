import argparse
import glob
import os
from lru import LRU
from greent.services.ontology import GenericOntology
from greent.servicecontext import ServiceContext
from flask import Flask, jsonify, g, Response, request
from flasgger import Swagger
from SPARQLWrapper import SPARQLWrapper, JSON
from greent.util import Curie_Resolver
app = Flask(__name__, instance_relative_config=True)

template = {
  "swagger": "2.0",
  "info": {
    "title": "Generic Ontology API",
    "description": "Onto is a facility which aggregates lookup services that provide generic facts about ontologies. It leverages the Uberongraph RDB (a SPARQL-queried Uberongraph available at https://stars-app.renci.org/uberongraph/#query) for data.",
    "contact": {
      "responsibleOrganization": "renci.org",
      "responsibleDeveloper": "scox@renci.org",
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
   'title': 'Onto API'
}

app.config['onto'] = {
    'config': "greent.conf",
    'data': "/data/",
    'debug': False,
}

swagger = Swagger(app, template=template)
cache = LRU(100)

class Core:
    
    """ Core ontology services. """
    def __init__(self):
        self.context = service_context = ServiceContext (config=os.environ.get('greent.conf'))
        self.generic_ont = GenericOntology(self.context, '') 

    def ont (self):
        return self.generic_ont
    
core = None

def get_ontology_service ():
    global core
    if not core:
        print (f"initializing core")
        core = Core ()
    result = core.ont()
    return result
  
def curie_normalize(curie):    
    assert ':' in curie, "Curie format invalid. Format should be <PREFIX>:<ID>"
    curie_parts = curie.split(':')
    print(curie_parts[0])
    prefix_list = list(Curie_Resolver.get_curie_to_uri_map().   keys())
    assert curie_parts[0].upper() in prefix_list, "Curie prefix not supported " \
                                       f"support prefixes are {prefix_list}"# since this is going to raise an exception in our sparql either way
    return ':'.join([curie_parts[0].upper()] + curie_parts[1:])



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
       description: "The name of an ontology for which you want all id's returned, e.g. MONDO."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /label/{{ input }}/
   responses:
     200:
       description: ...
   """
  ont = get_ontology_service ()
  return jsonify(ont.id_list(curie))


@app.route('/is_a/<curie>/<ancestors>')
def is_a (curie, ancestors):
   """ Determine ancestry.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: GO:2001317
       description: "An identifier from an ontology. eg, GO:2001317."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /is_a/{{ input }}/{{ input2 }}
     - name: ancestors
       in: path
       type: string
       required: true
       default: "MONDO:0004631"
       items:
         type: string
       description: "A comma separated list of identifiers. eg, GO:1901362"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /is_a/{{ input }}/{{ input2 }}
   responses:
     200:
       description: ...
   """
   if not curie:
       return jsonify({
        "error": "Curie must be supplied"
       }), 400
   if not isinstance(ancestors, str):
       return jsonify({
           "error": "Ancestors must be one or more identifiers"
       }) , 400
   ont = get_ontology_service ()
   is_a, ancestors = ont.is_a(curie, ancestors)
   return jsonify ({
       "is_a"      : is_a,
       "id"        : curie,
       "ancestors" : ancestors
   })

@app.route('/search/<pattern>')
def search (pattern):
   """ Search for terms in an ontology based on a pattern, optionally a regular expression. Look up is done on the synonyms, labels and definitions. Ids
   containing term in those properties are returned along with those properties.
   ---
   parameters:
     - name: pattern
       in: path
       type: string
       required: true
       default: "kidney"
       description: "Pattern to search for. .*kojic.*"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /search/{{ pattern }}/?regex={{ regex }}
     - name: regex
       in: query
       type: boolean
       required: true
       default: false
       description: Is the pattern a regular expession?
       x-valueType:
         - http://schema.org/boolean
       x-requestTemplate:
         - valueType: http://schema.org/boolean
           template: /search/{{ pattern }}/?regex={{ regex }}
   responses:
     200:
       description: ...
   """
   params = request.args
   regex = 'regex' in params and params['regex'] == 'true'
   ont = get_ontology_service ()  
   values = ont.search(pattern, regex)      
  
   return jsonify ({ "values" : values })
     
@app.route('/xrefs/<curie>')
def xrefs (curie):
   """ Get external references to other ontologies from this id.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Curie designating an ontology. eg, GO:2001317"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /xrefs/{{ curie }}/
   responses:
     200:
       description: ...
   """
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   ont = get_ontology_service ()
   return jsonify ({
       "xrefs"     : [ x.split(' ')[0] if ' ' in x else x for x in ont.xrefs (normalized_curie) ]
   } if ont else {})


@app.route('/lookup/<curie>')
def lookup (curie):
   """ Get ids for which this curie is an external reference.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "OMIM:143100"
       description: "Curie designating an external reference."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /lookup/{{ curie }}/
   responses:
     200:
       description: ...
   """
   ont = get_ontology_service ()
   try:
       refs = ont.lookup (curie)
   except AssertionError as error:
       error_message = str(error)
       return jsonify({"validation error": f"{error_message}"}), 400
   return jsonify ({
       "refs" : refs
   })
     
@app.route('/synonyms/<curie>')
def synonyms (curie):
   """ Get synonym terms for the given curie.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Curie designating an ontology. eg, GO:0000009"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /synonyms/{{ curie }}/
   responses:
     200:
       description: ...
   """
   result = []
   ont = get_ontology_service ()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   if ont:
       syns = ont.synonyms (normalized_curie)
       if syns:
           for syn in syns:
               result.append ({
                   "desc" : syn.get('desc', ''),
                   "scope" : syn.get('scope', ''),
                   "syn_type" : syn.get('type', None),
                   "xref"     : syn.get('xref', '')
               })
   return jsonify (result)

@app.route('/exactMatch/<curie>')
def exactMatch (curie):
   """ Use a CURIE to return a list of exactly matching IDs and or equivalent ontological classes.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Use a CURIE to find EXACTLY related CURIEs."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /exactMatch/{{ curie }}/
   responses:
     200:
       description: ...
   """
   ont = get_ontology_service ()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify ({'exact matches' : ont.exactMatch(normalized_curie)})

@app.route('/closeMatch/<curie>')
def closeMatch (curie):
   """ Use a CURIE to return a list of closely matching IDs.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Use a CURIE to find closely related CURIEs."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /closeMatch/{{ curie }}/
   responses:
     200:
       description: ...
   """
   ont = get_ontology_service ()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify ({'close matches' : ont.closeMatch(normalized_curie)})

@app.route('/subterms/<curie>')
def subterms (curie):
   """ Use a CURIE to return a list of ontological subterms.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Use a CURIE to find that term's subterms."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /subterms/{{ curie }}/
   deprecated: true
   responses:
     200:
       description: ...
   """
   ont = get_ontology_service()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify({ "subterms" : ont.subterms(normalized_curie) }  )

@app.route('/superterms/<curie>')
def superterms (curie):
   """ Use a CURIE to return a list of ontological superterms.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Use a CURIE to find that term's superterms."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /superterms/{{ curie }}/
   deprecated: true
   responses:
     200:
        description: ...
   """
   ont = get_ontology_service ()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify({ "superterms" : ont.superterms(normalized_curie) }  )

@app.route('/siblings/<curie>')
def siblings (curie):
   """ Use a CURIE to return a list of ontological siblings. Same as calling /children/{parent} for every parent gotten from /parents/<curie>.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Use a CURIE to find that term's siblings."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /siblings/{{ curie }}/
   responses:
     200:
        description: ...
   """
   ont = get_ontology_service ()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify({"siblings" : ont.siblings(normalized_curie)})

@app.route('/parents/<curie>')
def parents (curie):
   """ Use a CURIE to return a list of ontological parents (1st gen. ancestors).
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Use a CURIE to return a list of ontological parents (1st gen. ancestors)."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /parents/{{ curie }}/
   responses:
     200:
        description: ...
   """
   ont = get_ontology_service ()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify({"parents" : ont.parents(normalized_curie)})

@app.route('/property_value/<curie>/<path:property_key>')
def property_value (curie, property_key):
   """ Use a CURIE and a PROPERTY_KEY to retrieve the relevant PROPERTY_VALUE.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "CHEBI:30151"
       description: "Input a CURIE for which you want PROPERTY_VALUE information."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /property_value/{{ curie }}/{{ property_key }}

     - name: property_key
       in: path
       type: string
       required: true
       default: "http://purl.obolibrary.org/obo/chebi/inchikey"
       description: "Input a PROPERTY_KEY to retrieve PROPERTY_VALUE information for the above CURIE."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /property_value/{{ curie }}/{{ property_key }}
      
   responses:
     200:
        description: ...
   """

   ont = get_ontology_service()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify({"property_value" : ont.property_value(normalized_curie, property_key)})


@app.route('/all_properties/<curie>')
def all_properties (curie):
   """ Get ALL ontological properties for a CURIE.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Use a CURIE to return a list of all properties for the given CURIE."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /all_properties/{{ curie }}/
   responses:
     200:
        description: ...
   """
   ont = get_ontology_service()
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify({"all_properties" : ont.all_properties(normalized_curie)})
   
@app.route('/descendants/<curie>')
def descendants(curie):
  """ Get all cascading 'is_a' descendants of an input CURIE term.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: CHEBI:23367
       description: "Get all cascading 'is_a' descendants of an input CURIE term."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /descendants/{{ input }}/
   responses:
     200:
       description: ...
   """
  ont = get_ontology_service()
  try:
      normalized_curie = curie_normalize(curie)
  except AssertionError as error:
      error_msg = str(error)
      return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

  return jsonify(ont.descendants(normalized_curie))

@app.route('/ancestors/<curie>')
def ancestors(curie):
  """ Get all cascading 'is_a' anscestors of an input CURIE term.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: CHEBI:10001
       description: "Get all cascading 'is_a' ancestors of an input CURIE term."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /ancestors/{{ input }}/
   responses:
     200:
       description: ...
   """
  ont = get_ontology_service()
  try:
      normalized_curie = curie_normalize(curie)
  except AssertionError as error:
      error_msg = str(error)
      return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

  return jsonify(ont.ancestors(normalized_curie))

@app.route('/children/<curie>')
def children(curie):
  """ Return all outgoing (once-removed subterms) via SubClassOf from the Ontology Graph.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: GO:0005576
       description: "Return all outgoing (once-removed subterms) via SubClassOf from the Ontology Graph."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /children/{{ input }}/
   responses:
     200:
       description: ...
   """
  ont = get_ontology_service()
  try:
      normalized_curie = curie_normalize(curie)
  except AssertionError as error:
      error_msg = str(error)
      return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

  return jsonify(ont.children(normalized_curie))

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
  ont = get_ontology_service()
  try:
      normalized_curie = curie_normalize(curie)
  except AssertionError as error:
      error_msg = str(error)
      return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

  output = {'id':curie, 'label': ont.label(normalized_curie)}
  return jsonify(output)

@app.route('/uri/<curie>')
def uri_from_curie(curie):
   """ Expands a curie to uri.
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
   try:
       normalized_curie = curie_normalize(curie)
   except AssertionError as error:
       error_msg = str(error)
       return jsonify({"validation error": f"{error_msg}. Curie provided : `{curie}`"}), 400

   return jsonify({
     'uri': Curie_Resolver.curie_to_uri(normalized_curie)
   })

@app.route('/curie_uri_map')
def get_curie_uri_map():
   """ Gets the curie map used to convert curies to uri(s).
   ---
   responses:
     200:
       description: ...
    """
   return jsonify(
     Curie_Resolver.get_curie_to_uri_map()
    )


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Onto Server')
   parser.add_argument('-p', '--port',  type=int, help='Port to run service on.', default=5000)
   parser.add_argument('-d', '--debug', help="Debug.", default=False)
   parser.add_argument('-t', '--data',  help="Ontology data source.", default="/projects/stars/reasoner/var/ontologies/")
   parser.add_argument('-c', '--conf',  help='GreenT config file to use.', default="greent.conf")
   args = parser.parse_args ()
   app.config['SWAGGER']['greent_conf'] = args.greent_conf = args.conf
   app.config['onto'] = {
       'config' : args.conf,
       'data'   : args.data,
       'debug'  : args.debug,
   }
   app.run(host='0.0.0.0', port=args.port, debug=True, threaded=True)
