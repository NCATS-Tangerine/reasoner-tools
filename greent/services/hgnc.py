import requests
import json
from greent.service import Service
from greent.util import LoggingUtil

logger = LoggingUtil.init_logging(__name__)

class HGNC(Service):
    def __init__(self, name, context):
        super(HGNC,self).__init__(name, context)
        self.name = name
    def get_label(self, identifier):
        source, accessor = identifier.split(':')
        obj = requests.get(
            url = f"{self.url}/fetch/hgnc_id/{accessor}",
            headers = {
                "Accept" : "application/json"
            }).json ()
        val = obj.get("response", {}).get ("docs", [])[0]["symbol"]
        return { "label" : val }

    
