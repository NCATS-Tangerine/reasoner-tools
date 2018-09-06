from greent.service import Service
from greent.triplestore import TripleStore
from greent.util import LoggingUtil
from string import Template

logger = LoggingUtil.init_logging(__name__)

class MeshKS(Service):

    def __init__(self, context, url):
        super(MeshKS, self).__init__("mesh", context)
        self.triplestore = TripleStore (self.url)
        
    def get_label_by_id (self, term_id):
        result = self.triplestore.query_template (
            inputs = { "term_id" : term_id },
            outputs = [ 'label' ],
            template_text="""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
            PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
            PREFIX mesh2015: <http://id.nlm.nih.gov/mesh/2015/>
            PREFIX mesh2016: <http://id.nlm.nih.gov/mesh/2016/>
            PREFIX mesh2017: <http://id.nlm.nih.gov/mesh/2017/>
            PREFIX mesh2018: <http://id.nlm.nih.gov/mesh/2018/>
            SELECT DISTINCT ?label
            FROM <http://id.nlm.nih.gov/mesh>
            WHERE {
               VALUES (?id) { ( $term_id ) }
               ?id rdfs:label ?label .
            }
            ORDER BY ?label
            """)
          
        return list(map(lambda r : {
            'label'       : r['label']
        }, result))
