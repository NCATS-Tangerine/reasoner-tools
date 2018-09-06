import requests
import json
from greent.service import Service
from greent.util import LoggingUtil

logger = LoggingUtil.init_logging(__name__)

class PubChem(Service):
    def __init__(self, name, context):
        super(PubChem,self).__init__(name, context)
        self.name = name
    def get_label(self, identifier):
        obj = requests.get(
            url = f"{self.url}/rest/pug/substance/sid/{identifier}/synonyms/JSON",
            headers = {
                "Accept" : "application/json"
            }).json ()
        print (json.dumps(obj, indent=2))
        return {
            "label" : obj.get("InformationList",{}).get("Information", [{"Synonym":[""]}])[0]["Synonym"][0]
        }

    
