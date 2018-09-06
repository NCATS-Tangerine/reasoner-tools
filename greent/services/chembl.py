import requests
import json
from greent.service import Service
from greent.util import LoggingUtil

logger = LoggingUtil.init_logging(__name__)

class CHEMBL(Service):
    def __init__(self, name, context):
        super(CHEMBL,self).__init__(name, context)
        self.name = name
    def get_label(self, identifier):
        obj = requests.get(
            url = f"{self.url}/data/compound_record/{identifier}",
            headers = {
                "Accept" : "application/json"
            }).json ()
        return { "label" : obj.get("compound_name", "") }

    
