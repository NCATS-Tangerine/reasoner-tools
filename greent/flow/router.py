import argparse
import json
import requests
import os
import sys
import yaml
import time
import greent.flow.dag.conf as Conf
from greent.util import Resource
from jsonpath_rw import jsonpath, parse
import networkx as nx
import uuid
from networkx.algorithms import lexicographical_topological_sort

# scaffold
def read_json (f):
    obj = Resource.get_resource_obj(f, format="json")
    print (f"{obj}")
    return obj

class Router:
    ''' Route operator invocations through a common interface. '''
    ''' TODO: make this modular so that operators can be defined externally. Consider dynamic invocation. '''
    def __init__(self, workflow):
        self.r = {
            'naming.to_id' : self.naming_to_id,
            'gamma'        : self.gamma_query,
            'union'        : self.union
        }
        self.workflow = workflow
        self.prototyping_count = 0
        
    def route (self, context, job_name, op_node, op, args):
        ''' Invoke an operator known to this router. '''
        result = None
        if op in self.r:
            ''' Pass all operators context and the operation node. '''
            a = {
                "context" : context,
                "node"    : op_node
            }
            a.update (args)
            result = self.r[op](**a)
        else:
            raise ValueError (f"Unknown operator: {op}")
        return result

    def union (self, context, node, elements):
        return [ context.get_step(self, e)["result"] for e in elements ]

    def naming_to_id (self, context, node, type, input):
        ''' An interface to bionames for resolving words to ids. '''
        print (f"type: {type} input: {input}")
        input = context.resolve_arg (input)
        print (f"----> bionames input: {input}")
                
        bionames_request = requests.get(url = 'https://bionames.renci.org/lookup/'+input+'/'+type+'/', headers = {'accept': 'application/json'})
        bionames_request_json = bionames_request.json()
        return bionames_request_json
        
    def gamma_query (self, context, node, question, inputs):
        ''' An interface to the Gamma reasoner. '''
        # validate.

        ''' Build the query. '''
        select = inputs['select']
        jsonpath_query = parse (select)
        source = inputs['from']

        ''' Get the data source. '''
        operators = self.workflow.spec.get ("workflow", {})
        if not source in operators:
            print (f"Error: Source {source} not found in workflow.")
        if not "result" in operators[source]:
            if source in context.done:
                operators[source]["result"] = context.done[source]
        if not "result" in operators[source]:
            print (f"Error: Source {source} has not computed a result.")
        data_source = operators[source]["result"]
        print("")
        print (f"data source> {data_source}")
        
        ''' Execute the query. '''
        values = [ match.value for match in jsonpath_query.find (data_source) ]

        if 'where' in inputs and 'return' in inputs:
            return_col = inputs['return']
            collector = []
            where = inputs['where']
            filter_col, filter_value = where.split ('=')
            print(f"where: {filter_col} {filter_value}")
            columns = None
            filter_col_index = -1
            return_col_index = -1
            if "." in select:
                select_parts = select.split (".")
                last = select_parts[-1:][0]
                print (f"....{last}")
                if "," in last:
                    columns = last.split (",")
                    print (f".....{columns}")
                    for c, column in enumerate(columns):
                        print (f"column: {c} {column}")
                        if column == filter_col:
                            filter_col_index = c
                        if column == return_col:
                            return_col_index = c
            print (f"values: {values}")
            if filter_col_index > -1 and return_col_index > -1:
                for i in range(0, len(values), len(columns)):
                    actual_col_value = values[i + filter_col_index]
                    print (f"Actual col val {actual_col_value} at {i} + {filter_col_index}")
                    if actual_col_value == filter_value:
                        collector.append (values[ i + return_col_index ])
            else:
                print (f"Error: Must specify valid where clause and return together.")        
            values = collector

        if len(values) == 0:
            raise ValueError ("no values selected")

        # Read a cached local version.
        if os.path.exists ("gamma_answer_1.json"):
            answer = None
            with open("gamma_answer_1.json", "r") as stream:
                answer = json.loads (stream.read ())
            return answer
        if os.path.exists ("ranker.json"):
            answer = None
            with open("ranker.json", "r") as stream:
                answer = json.loads (stream.read ())
            return answer
    
        ''' Write the query. '''
        
        machine_question = {
            "machine_question": {
                "edges" : [],
                "nodes" : []
            }
        }

        ''' Get the list of transitions and add an input node with the selected values. '''
        ''' If machine questions don't handle lists, we'll need to work around this. '''
        ''' Set the type to the type of the first element of transitions. Document. '''
        ''' ckc, aug 21: Indeed, MQs do not handle first node lists.'''
        transitions = question["transitions"]
        node_id = 0
        print(data_source)
        if data_source:
            name = data_source[0]['label']
        else:
            name = ""
        print("")
        print("values:",values)
        # For NOW, we can only use a single curie value until Builder/Ranker accept more!
        machine_question["machine_question"]["nodes"].append ({
            "curie" : values[0],
            "id" : node_id,
            "name" : name,
            "type" : transitions[0]
        })
        for transition in transitions[1:]:
            node_id = node_id + 1
            machine_question["machine_question"]["nodes"].append ({
                "id" : node_id,
                "type" : transition
            })
            machine_question["machine_question"]["edges"].append ({
                "source_id" : node_id - 1,
                "target_id" : node_id
            })
        print (f"Gamma machine question: {json.dumps(machine_question,indent=2)}")

        ''' Send the query to Gamma and return result. '''
        query_headers = {
            'accept' : 'application/json',
            'Content-Type' : 'application/json'
        }
        print (f"executing builder query.")
        builder_task_id = requests.post(
            url = Conf.robokop_builder_build_url, \
            headers = query_headers,
            json = machine_question).json()
        print (f"{json.dumps(builder_task_id,indent=2)}")
        builder_task_id_string = builder_task_id["task id"]
        print (f"--------------")
        
        break_loop = False
        print("Waiting for builder to update the Knowledge Graph")
        while not break_loop:
          time.sleep(1)
          url = f"{Conf.robokop_builder_task_status_url}{builder_task_id_string}"
          builder_status = requests.get(url).json ()
          #print (f"{json.dumps(builder_status, indent=2)}-------------------\n")
          #print (f"{builder_status['status']}")
          print (f"{builder_status}")
          if isinstance(builder_status, dict) and builder_status['status'] == 'SUCCESS':
              break_loop = True
         
        answer = requests.post(
            url = Conf.robokop_ranker_answers_now_url, \
            headers = query_headers,
            json = machine_question).json()
        
        print (f"{json.dumps(answer,indent=2)}")
        with open("ranker.json", "w") as stream:
            stream.write (json.dumps (answer, indent=2))
            
        return answer
