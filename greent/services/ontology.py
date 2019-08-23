import pronto
import networkx
import obonet
import re
import logging
from orderedset import OrderedSet
from greent.util import LoggingUtil
from greent.service import Service
from pronto.relationship import Relationship
from greent.servicecontext import ServiceContext
from flask import jsonify
from SPARQLWrapper import SPARQLWrapper, JSON
from functools import reduce

logger = LoggingUtil.init_logging(__name__, level=logging.DEBUG)

class GenericOntology(Service):
    """ Sure, don't just dig around in obo files they say. But when the SPARQL is dry, we will drink straight from the obo if need be. """
    
    def run_sparql_query(self, query):
        logger.debug('Got sparql query')
        logger.debug(query)
        self.sparql_wrapper.setQuery(query)
        self.sparql_wrapper.setReturnFormat(JSON)
        results = self.sparql_wrapper.query().convert()

        keys = results['head']['vars']
        response = []
        for result in results['results']['bindings']:
            row = []
            for v in result:
                row.append(result[v]['value'].split('/')[-1].replace('_',':'))
            response.append(row)
        return keys, response


    def __init__(self, context, obo):
        """ Load an obo file. """
        super(GenericOntology, self).__init__("go", context)
        uberon_url = context.config.get_service ('uberongraph').get("url", None)
        self.sparql_wrapper = SPARQLWrapper(uberon_url)
        # self.ont = pronto.Ontology (obo)
        # self.obo_ont = obonet.read_obo(obo)
        
    def label(self,identifier):
        """Return the exitlabel for an identifier"""
        identifier_formatted = identifier.replace(':','_')
        query_text = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?labels
            FROM     <http://reasoner.renci.org/ontology>
            WHERE {{    
                <http://purl.obolibrary.org/obo/{identifier_formatted}> rdfs:label ?labels.               
            }}
        """
        headers, results = self.run_sparql_query(query_text)
        return results[0][0] if len(results) > 0 else ''
 
    def is_a(self,identifier, term):
        """Determine whether a term has a particular ancestor"""
        child_class = identifier.replace(':','_')        
        query_text = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?ancestors
            FROM     <http://reasoner.renci.org/ontology/closure>
            WHERE {    
                <http://purl.obolibrary.org/obo/PLACEHOLDER> rdfs:subClassOf ?ancestors.               
            }
            """        
        formatted_query_text = query_text.replace('PLACEHOLDER', child_class)
        headers, results = self.run_sparql_query(formatted_query_text)
        is_a = False 
        for x in results:
            for index, i in enumerate(headers):
                if x[index] == term:
                    is_a = True
            if is_a:
                break
        return is_a

    def single_level_is_a(self, identifier):
        """ Get single-level 'is_a' descendants. """
        result = []
        child_class = identifier.replace(':','_')
        uberongraph_request_url = 'https://stars-app.renci.org/uberongraph/sparql'
        sparql = SPARQLWrapper(uberongraph_request_url)
        query_text = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?ancestors
            FROM     <http://reasoner.renci.org/ontology>
            WHERE {    
                <http://purl.obolibrary.org/obo/PLACEHOLDER> rdfs:subClassOf ?ancestors
            }
            """        
        formatted_query_text = query_text.replace('PLACEHOLDER', child_class)
        headers, results = self.run_sparql_query(formatted_query_text)        
        response_curies = list(reduce(lambda x, y: x + y, results, []))
        return response_curies

    def descendants (self, identifier):
        """ This is also known as a recursive-'is_a' function, returning all levels below the input"""
        identifier_formatted = identifier.replace(':','_')
        query_text = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?term
            FROM     <http://reasoner.renci.org/ontology/closure>
            WHERE {{    
                ?term rdfs:subClassOf <http://purl.obolibrary.org/obo/{identifier_formatted}>
            }}
            """
        headers, results = self.run_sparql_query(query_text)
        result_list = reduce(lambda x, y : x + y, results, [])
        return result_list

    def xrefs(self, identifier):
        """ Get external references. """
        identifier = identifier.replace(':','_')
        query_text = f"""prefix xref: <http://www.geneontology.org/formats/oboInOwl#hasDbXref>
        SELECT DISTINCT ?xrefs
            FROM     <http://reasoner.renci.org/ontology>
            WHERE {{    
                <http://purl.obolibrary.org/obo/{identifier}> xref: ?xrefs
            }}
        """
        headers, results = self.run_sparql_query(query_text)
        results = list(map(lambda x : {'id': x } , reduce(lambda x, y : x + y, results, [])))
        return results
    
    def synonyms(self, identifier, curie_pattern=None):
        """ Get synonyms. """
        return \
            [ x for x in self.ont[identifier].synonyms if curie_pattern and x.startswith(curie_pattern) ] + \
            [ syn for syn in self.ont[identifier].synonyms ] \
            if identifier in self.ont else []
    
    def search (self, text, is_regex=False, ignore_case=True):
        """ Search for the text, treating it as a regular expression if indicated. """
        pat = None
        if is_regex:
            pat = re.compile(text, re.IGNORECASE) if ignore_case else re.compile(text)
        result = {}
        for term in self.ont:
            if is_regex:
                if pat.match (term.name):
                    logger.debug (f"  matched {text} pattern in term name: {term.name}")
                    result[term.id] = term
                else:
                    for syn in term.synonyms:
                        if pat.match (syn.desc):
                            logger.debug (f"  matched {text} pattern in synonym: {syn.desc}")
                            result[term.id] = term
            else:
                if text.lower() == term.name.lower():
                    logger.debug (f"  text {text} == term name {term.name}")
                    result[term.id] = term
                else:
                    for syn in term.synonyms:
                        if text.lower() == syn.desc.lower():
                            logger.debug (f"  text {text.lower()} == synonym: {syn.desc.lower()}")
                            result[term.id] = term
        result = [  { "id" : term.id, "label" : term.name } for key, term in result.items () ]
        return result
    
    def lookup(self, identifier):
        """ Given an identifier, find ids in the ontology for which it is an xref. """
        assert identifier and ':' in identifier, "Must provide a valid identifier."
        result = []
        for term in self.ont:
            xrefs = []
            if 'xref' in term.other:
                for xref in term.other['xref']:
                    if xref.startswith (identifier):
                        if ' ' in xref:
                            xref_pair = xref.split(' ')
                            xref_pair = [ xref_pair[0], ' '.join (xref_pair[1:]) ]
                        else:
                            xref_pair = [xref, '']
                        xrefs.append ({
                            'id'   : xref_pair[0],
                            'desc' : xref_pair[1]
                        })
            if len(xrefs) > 0:
                result.append ({
                    "id"    : term.id,
                    "xrefs" : xrefs
                })                
        return result

    def id_list(self, identifier):
        id_list = []
        id_list = [term.id for term in self.ont if term.id.startswith(identifier)]
        if not id_list:
            id_list = None
        return id_list

    def exactMatch(self, identifier):
        result = []
        if identifier in self.ont:
            term = self.ont[identifier]
            result = term.other['property_value']  if 'property_value' in term.other else []
        raw_exactMatches = [x.replace('exactMatch ', '') for x in result if 'exactMatch' in x]
        url_stripped_exactMatches = [re.sub(r"(https?:\/\/)(\s)*(www\.)?(\s)*((\w|\s)+\.)*([\w\-\s]+\/)", "", str(x)) for x in raw_exactMatches]
        formatted_exactMatches = [re.sub(r"(\/)",":", str(x)) for x in url_stripped_exactMatches]     
        # the umls URIs have a peculiar format, we handle that as follows:
        umls_exactMatches = [re.sub(r"(?:(resource:)|(id:))","", str(x)) for x in formatted_exactMatches if "resource" in x]
        normal_exactMatches = [x for x in formatted_exactMatches if "resource" not in x]
        all_exactMatches = normal_exactMatches + umls_exactMatches
        return all_exactMatches

    def closeMatch(self, identifier):
        result = []
        if identifier in self.ont:
            term = self.ont[identifier]
            result = term.other['property_value']  if 'property_value' in term.other else []
        raw_closeMatches = [x.replace('closeMatch ', '') for x in result if 'closeMatch' in x]
        url_stripped_closeMatches = [re.sub(r"(https?:\/\/)(\s)*(www\.)?(\s)*((\w|\s)+\.)*([\w\-\s]+\/)", "", str(x)) for x in raw_closeMatches]
        formatted_closeMatches = [re.sub(r"(\/)",":", str(x)) for x in url_stripped_closeMatches]     
        # the umls URIs have a peculiar format, we handle that as follows:
        umls_closeMatches = [re.sub(r"(?:(resource:)|(id:))","", str(x)) for x in formatted_closeMatches if "resource" in x]
        normal_closeMatches = [x for x in formatted_closeMatches if "resource" not in x]
        all_closeMatches = normal_closeMatches + umls_closeMatches
        return all_closeMatches

    def subterms(self, identifier):
        # networkx.ancestors returns SUBTERMS, check docs
        return self.descendants(identifier)

    def superterms(self, identifier):
        # networkx.descendants returns SUPERTERMS, check docs
        superterms = networkx.descendants(self.obo_ont, identifier)
        return list(superterms)

    def parents(self,identifier):
        predecessor_lineage = networkx.predecessor(self.obo_ont, identifier)
        parents = [key for key, value in predecessor_lineage.items() if identifier in value]
        return parents

    def children(self, identifier):
        print('ontology')
        successors = networkx.DiGraph.predecessors(self.obo_ont, identifier)
        children = list(successors)
        return children

    def siblings(self, identifier):
        predecessor_lineage = networkx.predecessor(self.obo_ont, identifier)
        parents = [key for key, value in predecessor_lineage.items() if identifier in value]
        sibling_lists = [networkx.DiGraph.predecessors(self.obo_ont, x) for x in parents]
        siblings = [list(x) for x in sibling_lists]
        siblings = [x for y in siblings for x in y]
        return siblings

    def property_value(self, identifier, property_key):
        """ Get properties """
        result = []
        if identifier in self.ont:
            term = self.ont[identifier]
            result = term.other['property_value']  if 'property_value' in term.other else []
        if ':' in property_key:
            property_key = property_key.split(':')[1]
        property_value = [x for x in result if property_key in x]
        result = property_value[0].split(" ")
        result = result[1]
        result = result[1:]
        result = result[:len(result)-1]
        return result

    def all_properties(self, identifier):
        """ Get ALL properties for a CURIE """
        if identifier in self.ont:
            term = self.ont[identifier]
            result = term.other
        return result