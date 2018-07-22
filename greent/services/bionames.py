import json
import requests
import traceback
import logging
from greent.service import Service
from greent.util import LoggingUtil
from builder.lookup_utils import chemical_ids_from_drug_names, lookup_disease_by_name

logger = LoggingUtil.init_logging(__name__, level=logging.DEBUG)

class BioNames(Service):
    """ BioNames services. """
    
    def __init__(self, context):
        """ Construct a bionames object and router for channeling searches. """
        super(BioNames, self).__init__("bionames", context)
        self.router = {
            "chemical_substance" : self._find_chemical_substance,
            "disease"            : self._find_disease,
            "phenotypic_feature" : self._find,
            "cell"               : self._find,
            "anatomical_entity"  : self._find,
            "gene"               : self._find
        }
        self.normalize = {
            "drug" : "chemical_substance",
            "medication" : "chemical_substance",
            "pharmaceutical" : "chemical_substance",
            "chemical substance" : "chemical_substance",
            "phenotypic feature" : "phenotypic_feature"
        }
        
    def lookup(self, q, concept=None):
        """ Lookup a term with an optional concept. """
        result = []
        if concept and not concept=="{concept}":
            """ Route the search by concept. """
            if concept in self.normalize:
                concept = self.normalize[concept]
            if concept in self.router:
                result = self.router[concept](q, concept)
            else:
                raise ValueError (f"Unknown concept {concept} is not a biolink-model concept.")
        else:
            """ Try everything? Union the lot. """
            for concept in self.router.keys():
                route = self.router[concept]
                result = result + route(q, concept)
        logger.debug (f"search q: {q} results: {result}")
        return result
    
    def _find_chemical_substance(self, q, concept):
        return chemical_ids_from_drug_names (q)
    
    def _find_disease(self, q, concept):
        return lookup_disease_by_name(q, concept)
        
        #return self._search_onto(q) + self._search_owlsim(q, concept)

    def _find(self, q, concept):
        return
    '''
    def _find_anatomical_entity(self, q, concept=None):
        return self._search_owlsim(q, concept) + self._search_onto(q)
    
    def _find_cell(self, q, concept):
        return  self._search_owlsim(q, concept) + self._search_onto(q)
    
    def _find_phenotypic_feature(self, q, concept):
        return self._search_onto(q) + self._search_owlsim(q, concept)
    
    def _find(self, q, concept):
        return self._search_onto(q, concept=concept) + self._search_owlsim(q, concept)
    
    def _search_owlsim(self, q, concept):
        result = []
        try:
            owlsim_query = f"https://owlsim.monarchinitiative.org/api/search/entity/autocomplete/{q}?rows=20&start=0&category={concept}"
            logger.debug (f"owlsim query: {owlsim_query}")
            response = requests.get (owlsim_query).json ()
            logger.debug (f"owlsim response: {response}")
            if response and "docs" in response:
                result = [ { "id" : d["id"], "label" : ", ".join (d["label"]), "type": concept } for d in response["docs"] ]
            logger.debug (f"owlsim result: {result}")
        except:
            traceback.print_exc ()
        return result
    
    def _search_onto(self, q, concept=None):
        result = []
        try:
            result = self.context.core.onto.search (q, is_regex=True, full=True)
            if concept:
                result = [r for r in result if r['type'] == concept]
        except:
            traceback.print_exc ()
        return result
    '''
