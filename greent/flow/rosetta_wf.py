import argparse
import json
import requests
import sys
import yaml
import time
from greent.util import Resource
from jsonpath_rw import jsonpath, parse


# scaffold
def read_json (f):
    obj = Resource.get_resource_obj(f, format="json")
    print (f"{obj}")
    return obj
'''
    r = None
    with open(f,'r') as stream:
        r = json.loads (stream.read ())
    return r
'''

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
        
    def route (self, context, op_node, op, args):
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
        return [ context.get_step(e)["result"] for e in elements ]

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
        operators = self.workflow.get ("workflow", {})
        if not source in operators:
            Env.error (f"Source {source} not found in workflow.")
        if not "result" in operators[source]:
            Env.error (f"Source {source} has not computed a result.")
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
                Env.error ("Must specify valid where clause and return together.")
                
            values = collector

        print("")    
        print (f"---gamma select--------> {values}")
        if len(values) == 0:
            raise ValueError ("no values selected")

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
        print("")
        print (f"Generated Gamma machine question: {json.dumps(machine_question,indent=2)}")

        ''' Send the query to Gamma and return result. '''
        print("")
        print("starting builder query")
        builder_query_url = "http://127.0.0.1:6010/api/"
        builder_query_headers = {
          'accept' : 'application/json',
          'Content-Type' : 'application/json'
          }
        
        robokop_query_data = machine_question
        builder_query_response = requests.post(robokop_builder_build_url, \
          headers = builder_query_headers, json = robokop_query_data)
        builder_task_id = builder_query_response.json()
        builder_task_id_string = builder_task_id["task id"]
        
        break_loop = False
        print("")
        print("Waiting for ROBOKOP Builder to update the Knowledge Graph")
        while not break_loop:
          time.sleep(1)
          builder_task_status_response = requests.get(robokop_builder_task_status_url+builder_task_id_string)
          builder_status = builder_task_status_response.json()
          if builder_status['status'] == 'SUCCESS':
            break_loop = True
         
        print("")
        print("Builder has finished updating the Knowledge Graph")
        print("")
        print("Sending the machine question to the ROBOKOP Ranker")
        ranker_now_query_headers = {
          'accept' : 'application/json',
          'Content-Type' : 'application/json'
          }
        robokop_query_data = machine_question
        ranker_now_query_response = requests.post(robokop_ranker_answers_now_url, \
          headers = builder_query_headers, json = robokop_query_data)
        self.ranker_answer = ranker_now_query_response.json()
        return self.ranker_answer  
        
class Env:
    ''' Process utilities. '''
    @staticmethod
    def exit (message, status=0):
        print (f"Exiting. {message}")
        sys.exit (status)
        
    @staticmethod
    def error (message):
        Env.exit (f"Error: {message}", 1)

    @staticmethod
    def log (message):
        print (message)

class Parser:
    ''' Parsing logic. '''
    def parse (self, f):
        result = None
        with open(f,'r') as stream:
            result = yaml.load (stream.read ())
        return result #return Resource.get_resource_obj (f)
    def parse_args (self, args):
        result = {}
        for a in args:
            if '=' in a:
                k, v = a.split ('=')
                result[k] = v
                Env.log (f"Adding workflow arg: {k} = {v}")
            else:
                Env.error (f"Arg must be in format <name>=<value>")
        return result

class Workflow:
    ''' Execution logic. '''
    def __init__(self, inputs, spec):
        assert spec, "Could not find workflow."
        self.router = Router (workflow=spec)
        self.inputs = inputs
        self.stack = []

    def push (self, op_node):
        self.stack.push (op_node)
    def pop (self):
        self.stack.pop ()
        
    def execute (self):
        ''' Execute this workflow. '''
        operators = self.router.workflow.get ("workflow", {})
        for operator in operators:
            print("")
            print (f"Executing operator: {operator}")
            op_node = operators[operator]
            op_code = op_node['code']
            args = op_node['args']
            op_node["result"] = self.router.route (self, op_node, op_code, args)
        return self.get_step("return")["result"]
    
    def get_step (self, name):
        return self.router.workflow.get("workflow",{}).get (name)
    
    def resolve_arg (self, name):
        ''' Find the value of an argument passed to the workflow. '''
        value = name
        if name.startswith ("$"):
            var = name.replace ("$","")
            if not var in self.inputs:
                Env.exit ("Referenced undefined variable: {var}")
            value = self.inputs[var]
            if "," in value:
                value = value.split (",")
        return value

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description='Rosetta Workflow')
    arg_parser.add_argument('-w', '--workflow', help='Workflow to run', default="wf.yaml")
    arg_parser.add_argument('-a', '--args', help='An argument', action="append")
    args = arg_parser.parse_args ()

    Env.log (f"Running workflow {args.workflow}")

    parser = Parser ()
    workflow = Workflow (
        inputs = parser.parse_args (args.args),
        spec = parser.parse (args.workflow))
    result = workflow.execute ()
    print (f"result> {json.dumps(result,indent=2)}")
    
    # python parser.py -w mq2.yaml -a drug_name=imatinib
