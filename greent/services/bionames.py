import json
import requests
import traceback
import logging
from greent.service import Service
from greent.services.mesh import MeshKS
from greent.servicecontext import ServiceContext
from greent.util import LoggingUtil
from builder.lookup_utils import chemical_ids_from_drug_names

logger = LoggingUtil.init_logging(__name__, level=logging.DEBUG)

class BioNames(Service):
    """ BioNames services. """
    
    def __init__(self, context):
        """ Construct a bionames object and router for channeling searches. """
        super(BioNames, self).__init__("bionames", context)
        self.router_directory = {
            "chemical_substance"                : self._find_chemical_substance,
            "disease"                           : self._find,
            "phenotypic_feature"                : self._find,
            "cell"                              : self._find,
            "anatomical_entity"                 : self._find,
            "gene"                              : self._find,
            "biological_process_or_activity"    : self._find
        }
        self.normalize = {
            "drug" : "chemical_substance",
            "metabolite" : "chemical_substance",
            "medication" : "chemical_substance",
            "pharmaceutical" : "chemical_substance",
            "chemical substance" : "chemical_substance",
            "phenotypic feature" : "phenotypic_feature",
            "phenotype feature" : "phenotypic_feature",
            "phenotype" : "phenotypic_feature",
            "phenotypic_trait" : "phenotypic_feature",
            "phenotypic trait" : "phenotypic_feature",
            "phenotype trait" : "phenotypic_feature",
            "anatomical entity" : "anatomical_entity",
            "biological process" : "biological_process_or_activity",
            "Molecular Activity" : "biological_process_or_activity",
            "genetic_condition" : "disease"
        }
        
    def lookup_router(self, q, concept=None):
        """ Lookup a term with an optional concept. """
        result = []
        if concept and not concept=="{concept}":
            """ Route the search by concept. """
            if concept in self.normalize:
                concept = self.normalize[concept]
            if concept in self.router_directory:
                result = self.router_directory[concept](q, concept)
            else:
                raise ValueError (f"Unknown concept {concept} is not a biolink-model concept.")
        else:
            """ Try everything? Union the lot. """
            for concept in self.router_directory.keys():
                route = self.router_directory[concept]
                result = result + route(q, concept)
        #logger.debug (f"search q: {q} results: {result}")
        return result
    
    def _find_chemical_substance(self, q, concept):
        return chemical_ids_from_drug_names (q)
    
    def _find(self, q, concept):
        all_find_results_filtered = []
        all_find_results = self._search_onto(q, concept=concept) + self._search_monarch(q, concept)
        for x in all_find_results:
            label = x['label'].lower()
            if q.lower() in label:
                if x['id'] not in str(all_find_results_filtered):
                    all_find_results_filtered.append(x)
        return all_find_results_filtered

    def _search_monarch(self, q, concept):
        result = []
        try:
            monarch_query = f"http://api.monarchinitiative.org/api/search/entity/autocomplete/{q}&category={concept}"
            #logger.debug (f"monarch query: {monarch_query}")
            response = requests.get (monarch_query).json ()
            if response:
                for x in response['docs']:
                    for key, value in x.items():
                        if key == 'category':
                            if len(value) > 1 and value[0] == concept:            
                                new_dict = {'id' : x['id'], 'label' : x['label'][0], 'type' : x['category'][0]}
                                result.append(new_dict)
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

    def ID_to_label_lookup(self, ID):
        result = []
        onto_result = []
        mesh_result = []
        if ID.startswith('MESH'):
            try:
                ID_split = ID.split(':')
                ID_split[0] = ID_split[0].lower()
                mesh_ID_formatted = ID_split[0]+':'+ID_split[1]
                url = "http://id.nlm.nih.gov/mesh/sparql"
                mesh_response = MeshKS(ServiceContext.create_context(), url).get_label_by_id(mesh_ID_formatted)
                mesh_result = result + [{ "id" : ID, "label" : mesh_response[0]['label']} ]
            except:
                traceback.print_exc ()
        else:
            try:
                onto_result = result + [ { "id" : ID, "label" : self.context.core.onto.get_label (ID) }]
            except:
                traceback.print_exc ()
        all_results = onto_result + mesh_result
        return all_results