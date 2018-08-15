# input = chemical ID or chemical name as string
# output = json object suitable for input to "machine_question" format 

import json
import requests
import traceback
import logging
from greent.service import Service
from greent.util import LoggingUtil

class query_to_graph(Service):
#orchestrator is the subclass
#Service is the parent or "super" class
    def __init__(self, context):
        super(query_to_graph, self).__init__("query_to_graph", context)

    def invoke (query, graph, graph_filters):
        print (f"query: {query} graph: {graph} graph_filters: {graph_filters}")


    def builder_query_1 ():
        print('test builder_query_1')
        return

query_to_graph.build_query_1()
