import argparse
import glob
import os
from lru import LRU
from greent.services.ontology import GenericOntology
from greent.servicecontext import ServiceContext
from flask import Flask, jsonify, g, Response, request
from flasgger import Swagger
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__, instance_relative_config=True)

template = {
  "swagger": "2.0",
  "info": {
    "title": "Generic Ontology API",
    "description": "Generic facts about ontologies (Flask/Gunicorn). This interface utilizes flat file .obo files as well as leveraging the Uberongraph RDB (a SPARQL-queried Uberongraph available at https://stars-app.renci.org/uberongraph/#query)",
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

swagger = Swagger(app, template=template)
cache = LRU(100)

class Core:
    
    """ Core ontology services. """
    def __init__(self):
        self.onts = {}
        # self.context = service_context = ServiceContext (
        #     config=app.config['SWAGGER']['greent_conf'])
        self.context = service_context = ServiceContext (config=os.environ.get('greent.conf'))

        # the glob.glob method was not working for gunicorn loading of app
        # thus, the ontology_files are now hard-coded
        # as we want to move towards the direct use of UberonGraph-->UberOnto in
        # the future, I do not see this as a horrible hack
        # ontology_files = ['chebi.obo', 'cl.obo','go.obo','hp.obo','mondo.obo', 'ro.obo', 'uberon.obo']
        # for f in ontology_files:
        #     print (f"loading {f}")
        #     f = '../../'+f #the glob.glob method was not working for gunicorn loading of app
        #     file_name = os.path.basename (f)
        #     name = file_name.replace (".obo", "")
        #     self.onts[name] = GenericOntology(self.context, f)
        #     cache[f] = self.onts[name]

        data_dir = app.config['onto']['data']
        data_pattern = os.path.join (data_dir, "*.obo")
        ontology_files = glob.glob (data_pattern)
        for f in ontology_files:
            print (f"loading {f}")
            file_name = os.path.basename (f)
            name = file_name.replace (".obo", "")
            self.onts[name] = GenericOntology(self.context, f)
            cache[f] = self.onts[name]

    def ont (self, curie):
        return self.onts[curie.lower()] if curie and curie.lower() in self.onts else None
    
core = None

def get_core (curie=None):
    global core
    if not core:
        print (f"initializing core")
        core = Core ()
    result = core
    if curie:
        if ":" in curie:
            curie = curie.split(":")[0]
        result = core.ont (curie)
    return result

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
           template: /label/{{ input }}/
   responses:
     200:
       description: ...
   """
  ont = get_core (curie)
  return jsonify(ont.id_list(curie))

@app.route('/single_level_is_a/<curie>')
def single_level_is_a (curie):
   """ Use a CURIE to return a list of the direct, single-hop, 'is_a' descendants of the input term.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "GO:0005576"
       description: "Use a CURIE to return a list of the direct, single-hop, 'is_a' descendants of the input term."
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /single_level_is_a/{{ curie }}/
   responses:
     200:
       description: ...
   """
   ont = get_core (curie)
   return jsonify ({'single_level_is_a' : ont.single_level_is_a(curie)})

@app.route('/is_a/<curie>/<ancestors>/')
def is_a (curie, ancestors):
   """ Determine ancestry.
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: GO:2001317
       description: "An identifier from an ontology. eg, GO:2001317"
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
   assert curie, "An identifier must be supplied."
   assert isinstance(ancestors, str), "Ancestors must be one or more identifiers"
   ont = get_core (curie)
   return jsonify ({
       "is_a"      : ont.is_a(curie, ancestors),
       "id"        : curie,
       "ancestors" : ancestors
   })

@app.route('/search/<pattern>/')
def search (pattern):
   """ Search for ids in an ontology based on a pattern, optionally a regular expression.
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
   core = get_core ()
   
   obo_map = {
       'chebi'   : 'chemical_substance',
       'pubchem' : 'chemical_substance',
       'mondo'   : 'disease',
       'hp'      : 'phenotypic_feature',
       'go'      : 'biological_process_or_activity',
       'uberon'  : 'anatomical_entity',
       'cl'      : 'cell',
       'doid'    : 'disease',
       'ro'      : 'related_to'
   }
   vals = []
   for name, ont in core.onts.items():
       new = ont.search(pattern, regex)
       for n in new:
           n['type'] = obo_map[name] if name in obo_map else 'unknown'
       vals.extend(new)
   return jsonify ({ "values" : vals })
     
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
   ont = get_core (curie)
   return jsonify ({
       "xrefs"     : [ x.split(' ')[0] if ' ' in x else x for x in ont.xrefs (curie) ]
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
   core = get_core ()
   return jsonify ({
       "refs" : [ ref for name, ont in core.onts.items() for ref in ont.lookup (curie) ]
   })
     
@app.route('/synonyms/<curie>/')
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
   ont = get_core (curie)
   if ont:
       syns = ont.synonyms (curie)
       if syns:
           for syn in syns:
               result.append ({
                   "desc" : syn.desc,
                   "scope" : syn.scope,
                   "syn_type" : syn.syn_type.name if syn.syn_type else None,
                   "xref"     : syn.xref
               })
   return jsonify (result)

@app.route('/exactMatch/<curie>')
def exactMatch (curie):
   """ Use a CURIE to return a list of exactly matching IDs.
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
   ont = get_core (curie)
   return jsonify ({'exact matches' : ont.exactMatch(curie)})

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
   ont = get_core (curie)
   return jsonify ({'close matches' : ont.closeMatch(curie)})

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
   responses:
     200:
       description: ...
   """
   ont = get_core (curie)
   return jsonify({ "subterms" : ont.subterms(curie) }  )

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
   responses:
     200:
        description: ...
   """
   ont = get_core (curie)
   return jsonify({ "superterms" : ont.superterms(curie) }  )

@app.route('/siblings/<curie>')
def siblings (curie):
   """ Use a CURIE to return a list of ontological siblings.
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
   ont = get_core (curie)
   return jsonify({"siblings" : ont.siblings(curie)})

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
       description: "Use a CURIE to return a list of ontological parents (1st gen. ancestors)"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /parents/{{ curie }}/
   responses:
     200:
        description: ...
   """
   ont = get_core (curie) 
   return jsonify({"parents" : ont.parents(curie)})

@app.route('/property_value/<curie>/<path:property_key>/')
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

   ont = get_core (curie)

   return jsonify({"property_value" : ont.property_value(curie, property_key)})


@app.route('/all_properties/<curie>')
def all_properties (curie):
   """ Get ALL properties for a CURIE
   ---
   parameters:
     - name: curie
       in: path
       type: string
       required: true
       default: "MONDO:0004634"
       description: "Use a CURIE to return a list of all properties for the given CURIE"
       x-valueType:
         - http://schema.org/string
       x-requestTemplate:
         - valueType: http://schema.org/string
           template: /all_properties/{{ curie }}/
   responses:
     200:
        description: ...
   """
   ont = get_core (curie) 
   return jsonify({"all_properties" : ont.all_properties(curie)})
   
##################
# start of sparkle based access to the Uberongraph RDB
##################

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
   #parser.add_argument('-t', '--data',  help="Ontology data source.", default="c:/Users/powen/PycharmProjects/Reasoner/reasoner-tools/")
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
