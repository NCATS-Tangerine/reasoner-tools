import pronto
import networkx
import obonet
import re
import logging
from orderedset import OrderedSet
from greent.util import LoggingUtil, Curie_Resolver
from greent.service import Service
from pronto.relationship import Relationship
from greent.servicecontext import ServiceContext
from flask import jsonify
from greent.triplestore import TripleStore
from SPARQLWrapper import SPARQLWrapper, JSON
from functools import reduce

logger = LoggingUtil.init_logging(__name__, level=logging.DEBUG)

class GenericOntology(Service):
    """ Sure, don't just dig around in obo files they say. But when the SPARQL is dry, we will drink straight from the obo if need be. """

    def __init__(self, context, obo):
        """ Load an obo file. """
        super(GenericOntology, self).__init__("go", context)
        self.url = context.config.get_service ('uberongraph').get("url", None)
        self.triplestore = TripleStore(self.url)
        self.sparql_wrapper = SPARQLWrapper(self.url)
        curie_prefix_map = Curie_Resolver.get_curie_to_uri_map()
        self.resolve_uri = Curie_Resolver.uri_to_curie
        self.ontology_prefixes = list(map(lambda x : f'PREFIX {x}: <{curie_prefix_map[x]}>', curie_prefix_map))


    def add_sparql_prefixes(self, query_template):
        return  '\n'.join(self.ontology_prefixes) + '\n' + query_template

    def run_sparql_query_raw(self, query):
        query = self.add_sparql_prefixes(query)
        self.sparql_wrapper.setQuery(query)
        self.sparql_wrapper.setReturnFormat(JSON)
        results = self.sparql_wrapper.query().convert()
        return results

    def query_sparql(self, query_template, inputs, outputs):
        # prepend prefixes here to avoid every one doing the same thing
        q = self.add_sparql_prefixes(query_template)
        logger.error(q)
        return self.triplestore.query_template(
            template_text = q,
            inputs = inputs,
            outputs = outputs
        )


    def label(self,identifier):
        """Return the exitlabel for an identifier"""       
        query_text = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?labels
            FROM     <http://reasoner.renci.org/ontology>
            WHERE {{    
               $identifier rdfs:label ?labels.               
            }}
        """
        results = self.query_sparql(
            query_text,
            inputs = {
                'identifier': identifier
            },
            outputs = ['labels']
        )
        return results[0]["labels"]
        
 
    def is_a(self,identifier, ancestors):
        """Determine whether a term has a particular ancestor"""
        query_template =lambda ancestor: f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            ASK
            FROM <http://reasoner.renci.org/ontology/closure>
            FROM <http://reasoner.renci.org/ontology>
            WHERE {{    
                {identifier} rdfs:subClassOf {ancestor}.               
            }}
            """
        result = []
        for ancestor in ancestors.split(','):
            ancestor = ancestor.strip(' ')
            response = self.run_sparql_query_raw(
                query_template(ancestor)
            )            
            if response['boolean']:
                result.append(ancestor)        
        is_a = len(result) > 0
        return is_a , result
        

    def single_level_is_a(self, identifier):
        """ Get single-level 'is_a' descendants. """
        query_text = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ID: <http://www.geneontology.org/formats/oboInOwl#id>
            SELECT DISTINCT ?descendant ?descendant_id
            FROM     <http://reasoner.renci.org/ontology>
            WHERE {    
              ?descendant rdfs:subClassOf  $identifier
              OPTIONAL {                
                ?descendant ID: ?descendant_id
              }
            }
            """     
        results = self.query_sparql(
            query_text,
            inputs = {
                'identifier': identifier
            },
            outputs = [
                'descendant',
                'descendant_id'
            ]
        )      
        response_curies = reduce(lambda x, y: x + [y['descendant_id'] if 'descendant_id' in y else self.resolve_uri(y['descendant'])], results, [])
        return response_curies


    def descendants (self, identifier):
        """ This is also known as a recursive-'is_a' function, returning all levels below the input"""        
        query_text = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ID: <http://www.geneontology.org/formats/oboInOwl#id>
            SELECT DISTINCT ?descendant ?descendant_id
            FROM <http://reasoner.renci.org/ontology/closure>
            WHERE {{    
                ?descendant rdfs:subClassOf $identifier.
                OPTIONAL {{ ?descendant ID: ?descendant_id. }}
            }}
            """
        results = self.query_sparql(
            query_template = query_text,
            inputs = {
                'identifier': identifier
            },
            outputs = [
                'descendant',
                'descendant_id'
            ]
        )
        
        result_list = reduce(lambda x, y : x + [y['descendant_id'] if 'descendant_id' in y else self.resolve_uri(y['descendant'])], results, [])
        return result_list
    

    def ancestors(self, identifier):
         """ This is also known as a recursive-'is_a' function, returning all levels below the input"""        
         query_text = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ID: <http://www.geneontology.org/formats/oboInOwl#id>
            SELECT DISTINCT ?ancestor ?ancestor_id
            FROM <http://reasoner.renci.org/ontology/closure>
            WHERE {{    
                $identifier  rdfs:subClassOf ?ancestor.
                OPTIONAL {{
                    ?ancestor ID: ?ancestor_id.
                }}
            }}
            """
         results = self.query_sparql(
            query_template = query_text,
            inputs = {
                'identifier': identifier
            },
            outputs = [
                'ancestor',
                'ancestor_id'
            ]
         )
         result_list = reduce(lambda x, y : x + [y['ancestor_id'] if 'ancestor_id' in y else self.resolve_uri(y['ancestor'])], results, [])
         return result_list


    def xrefs(self, identifier):
        """ Get external references. """
        query_text = f"""prefix xref: <http://www.geneontology.org/formats/oboInOwl#hasDbXref>
        SELECT DISTINCT ?xrefs
            FROM     <http://reasoner.renci.org/ontology>
            WHERE {{    
                $identifier xref: ?xrefs
            }}
        """
        results = self.query_sparql(
            query_template = query_text,
            inputs = {
                'identifier': identifier
            },
            outputs = [
                'xrefs'
            ]
        )
        results = reduce(lambda x, y : x + [y['xrefs']], results, [])
        return results
    

    def synonyms(self, identifier, curie_pattern=None):
        """ Get synonyms. """
        query_template = lambda predicate: f"""
        PREFIX RELATED_SYNONYM: <http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym>
        PREFIX EXACT_SYNONYM: <http://www.geneontology.org/formats/oboInOwl#hasExactSynonym>
        PREFIX XREF: <http://www.geneontology.org/formats/oboInOwl#hasDbXref>
        PREFIX DEFENITION: <http://purl.obolibrary.org/obo/IAO_0000115>
        SELECT DISTINCT ?desc ?xref ?defn
        WHERE {{
            $identifier {predicate} ?desc.
            OPTIONAL {{
                ?desc XREF: ?xref.
                ?desc DEFENITION: ?defn.
             }}
        }}
        """
        exact = self.query_sparql(
            query_template = query_template("EXACT_SYNONYM:"),
            inputs = { 
                'identifier': identifier
            }, outputs = [
                'desc',
                'xref',
                'defn'
            ]
        )
        for row in exact:
            row['scope'] = 'EXACT'
        related =  self.query_sparql(
            query_template = query_template("RELATED_SYNONYM:"),
            inputs = { 
                'identifier': identifier
            }, outputs = [
                'desc',
                'xref',
                'defn'
            ]
        )
        for row in related:
            row['scope'] = 'RELATED'
        return exact + related

    def search (self, text, is_regex=False, ignore_case=True):
        """ Search for the text, treating it as a regular expression if indicated. """
        search_string = text
        if is_regex and ignore_case: 
            filtr = f"""
                (
                   regex(str(?definition), "$search_string","i") || 
                   regex(str(?label), "$search_string","i") ||
                   regex(str(?related_synonym), "$search_string","i") ||
                   regex(str(?exact_synonym), "$search_string","i")
                )"""
        elif is_regex and not ignore_case:
            filtr = f"""
                (
                   regex(str(?definition), "$search_string") || 
                   regex(str(?label), "$search_string") ||
                   regex(str(?related_synonym), "$search_string") ||
                   regex(str(?exact_synonym), "$search_string")
                )
            """
        elif not is_regex and ignore_case:
            search_string = search_string.lower()
            filtr = f"""
                (
                    lcase(str(?label))= "$search_string" ||
                    lcase(str(?definition))= "$search_string" ||
                    lcase(str(?related_synonym))= "$search_string" ||
                    lcase(str(?exact_synonym))= "$search_string" 
                )
                    """
        else:
            filtr = f"""
                (
                    str(?label) = "$search_string" ||
                    str(?definition) = "$search_string" ||
                    str(?exact_synonym) = "$search_string" ||
                    str(?related_synonym) = "$search_string" 
                )"""


        query_text = f"""
        PREFIX DEFINED_BY: <http://www.w3.org/2000/01/rdf-schema#isDefinedBy>
        PREFIX DEFINITION: <http://purl.obolibrary.org/obo/IAO_0000115>
        PREFIX RELATED_SYNONYM: <http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym>
        PREFIX EXACT_SYNONYM: <http://www.geneontology.org/formats/oboInOwl#hasExactSynonym>        
        SELECT DISTINCT ?id ?label ?definition ?defined_by        
        WHERE {{
            OPTIONAL{{
                ?id EXACT_SYNONYM: ?exact_synonym.                
            }}
            OPTIONAL {{
                ?id RELATED_SYNONYM: ?related_synonym.
            }}          
            OPTIONAL {{
                ?id rdfs:label ?label.
            }}
            OPTIONAL {{
                ?id DEFINITION: ?definition.
            }}
            OPTIONAL {{
                ?id DEFINED_BY: ?defined_by.
            }}
            FILTER {filtr}.
        }}
        """
        response = self.query_sparql(
            query_template = query_text,
            inputs = {
                'search_string': search_string
            }, outputs = [
                'id',
                'label',
                'defined_by',
                'definition'
            ]
        )
        for row in response:
            row['id'] = Curie_Resolver.uri_to_curie(row['id'])
        return response
    

    def lookup(self, identifier):
        """ Given an identifier, find ids in the ontology for which it is an xref. """
        assert identifier and ':' in identifier, "Must provide a valid identifier."
        query_template = """
        PREFIX XREF: <http://www.geneontology.org/formats/oboInOwl#hasDbXref>
        PREFIX LABEL: <http://www.w3.org/2000/01/rdf-schema#label>
        PREFIX ID: <http://www.geneontology.org/formats/oboInOwl#id>
                SELECT DISTINCT  ?xrefs ?term_id ?term_label
                    FROM     <http://reasoner.renci.org/ontology>
                    WHERE {
                    ?term XREF: ?o;
                            XREF: ?xrefs;
                            ID: ?term_id;
                            LABEL: ?term_label.
                    FILTER(?o = '$identifier' && !isBlank(?term)).               
                    } 
        """
        result = self.query_sparql(
            query_template = query_template,
            inputs= {
                'identifier': identifier
            }, outputs = [
                'xrefs',
                'term_id',
                'term_label'
            ]
        )
        response = []
        buffer = {}
        for row in result:
            if row['term_id'] not in buffer:
                buffer[row['term_id']] = {
                    'label': row['term_label'],
                    'xrefs': []
                }
            xref = row['xrefs']
            buffer[row['term_id']]['xrefs'] += [row['xrefs']]  if row['xrefs'] not in buffer[row['term_id']]['xrefs'] else [] 
        for term_id in buffer:
            response.append({
                'id': term_id,
                'label': buffer[term_id]['label'],
                'xrefs': buffer[term_id]['xrefs']

            })           
        return response


    def id_list(self, identifier):
        identifier_uri = Curie_Resolver.get_curie_to_uri_map().get(identifier.upper(), None)
        if identifier_uri == None:
            return []
        query = f"""
                PREFIX TYPE: <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
                PREFIX CLASS: <http://www.w3.org/2002/07/owl#Class>
                PREFIX ID: <http://www.geneontology.org/formats/oboInOwl#id>
                SELECT DISTINCT ?term ?term_id
                FROM <http://reasoner.renci.org/ontology>
                        WHERE {{
                        ?term TYPE: CLASS:.
                        FILTER (strstarts(lcase(str(?term)), lcase("$identifier")))
                        OPTIONAL {{
                            ?term ID: ?term_id #try to get the id from sparql else parse ?? 
                        }}
                        }} 
                """
        result = self.query_sparql(
            query_template = query,
            inputs = {
                'identifier': identifier_uri
            }, outputs =[
                'term',
                'term_id'
            ]
        ) 
        return reduce(lambda x, y: x + [y['term_id'] if 'term_id' in y else self.resolve_uri(y['term'])], result, [])
       


    def exactMatch(self, identifier):
        #if ontolgies are missing we should be looking here        
        query_string = lambda predicate: f"""
            PREFIX EXACT_MATCH: <http://www.w3.org/2004/02/skos/core#exactMatch>
            PREFIX EQUIVALENT_CLASS: <http://www.w3.org/2002/07/owl#equivalentClass>
            PREFIX ID: <http://www.geneontology.org/formats/oboInOwl#id>
            SELECT DISTINCT ?match ?match_id
            FROM <http://reasoner.renci.org/ontology>
                    WHERE {{
                     $identifier {predicate} ?match.      
                     OPTIONAL {{
                         ?match ID: ?match_id.
                     }} 
                     FILTER (!isBlank(?match)) #This sometimes returns blank nodes         
                    }} 
            """
        result = reduce(lambda x, y: x + [y['match_id'] if 'match_id' in y else self.resolve_uri(y['match'])], self.query_sparql(
            query_template = query_string('EXACT_MATCH:'),
            inputs = {
                'identifier': identifier
            }, outputs = [
                'match',
                'match_id'
            ]
        ), [])
        result += list(filter( lambda x : x not in result, reduce(lambda x, y: x + [y['match_id'] if 'match_id' in y else self.resolve_uri(y['match'])], self.query_sparql(
            query_template = query_string('EQUIVALENT_CLASS:'),
            inputs = {
                'identifier': identifier
            }, outputs = [
                'match',
                'match_id'
            ]
        ), [])))
        return result


    def closeMatch(self, identifier):
        query_template = """
            PREFIX CLOSE_MATCH: <http://www.w3.org/2004/02/skos/core#closeMatch>
            PREFIX ID: <http://www.geneontology.org/formats/oboInOwl#id>
            SELECT DISTINCT ?match ?match_id
            FROM <http://reasoner.renci.org/ontology>
                    WHERE {
                     $identifier CLOSE_MATCH: ?match.      
                     OPTIONAL {
                         ?match ID: ?match_id.
                     } 
                     FILTER (!isBlank(?match)) #This sometimes returns blank nodes         
                    } 
        """
        results = reduce( lambda x, y: x  + [y['match_id'] if 'match_id' in y else self.resolve_uri(y['match'])], self.query_sparql(
            query_template = query_template,
            inputs = {
                'identifier': identifier
            }, outputs = [
                'match',
                'match_id'
            ]
        ), [])
        return results

   
    def subterms(self, identifier):
        return self.descendants(identifier)


    def superterms(self, identifier):
        return self.ancestors(identifier)


    def parents(self,identifier):
        """First generation ancestors"""
        query_template = f"""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ID: <http://www.geneontology.org/formats/oboInOwl#id>
            SELECT DISTINCT ?parent ?parent_id
            FROM     <http://reasoner.renci.org/ontology>
            WHERE {{    
             $identifier  rdfs:subClassOf  ?parent.
             OPTIONAL {{
                 ?parent ID: ?parent_id
             }} 
            FILTER(!isBlank(?parent))
            }}"""
        result = reduce(lambda x, y: x + [y['parent_id'] if 'parent_id' in y else self.resolve_uri(y['parent'])],
        self.query_sparql(
            query_template = query_template,
            inputs = {
                'identifier': identifier
            }, outputs = [
                'parent',
                'parent_id'
            ]
        ), [])
        return result


    def children(self, identifier):
        """first generation descedants"""
        result = self.single_level_is_a(identifier)
        return result


    def siblings(self, identifier):
        """
        Common parents 
        """
        parents = self.parents(identifier)
        sibilings = []
        for parent in parents:
            sibilings += list(filter(lambda x: x != identifier and x not in sibilings, self.children(parent if 'http' not in parent else f'<{parent}>')))
        return sibilings


    def property_value(self, identifier, property_key):
        """ Get properties """
        query_template = """
        SELECT ?property_value 
        WHERE {
            $identifier <$property_key> ?property_value.
        }
        """
        result = self.query_sparql(
            query_template  = query_template,
            inputs = {
                'identifier': identifier,
                'property_key': property_key
            },
            outputs = [
                'property_value'
            ]
        )
        response =  reduce(lambda x, y: x + [y['property_value']], result, [])
        if len(response) == 1:
            return response[0]
        else: return response


    def all_properties(self, identifier):
        """ Get ALL properties for a CURIE """
        query_template = """
        SELECT ?property_key ?property_value ?property_label
        FROM <http://reasoner.renci.org/ontology>
        WHERE
         {
            $identifier ?property_key ?property_value.
            OPTIONAL {
                ?property_key rdfs:label ?property_label.
                }
            FILTER (!isBlank(?property_value))
        }
        """
        results = self.query_sparql(
            query_template = query_template,
            inputs = {
                'identifier': identifier
            }, outputs = {
                'property_value',
                'property_key',
                'property_label'
            }
        )
        # group it by property label for those which have label 
        grouped = {}
        for row in results: 
            label = row['property_label'] if 'property_label' in row else None
            key = row['property_key']
            if key not in grouped:
                grouped[key] = {
                    'property_label' : label,
                    'property_values': []
                }
            if row['property_value'] not in grouped[key]['property_values']:
                grouped[key]['property_values'].append(row['property_value'])
            for key in grouped:
                grouped[key].update({'property_key': key})            
        return list(map(lambda x : grouped[x], grouped))