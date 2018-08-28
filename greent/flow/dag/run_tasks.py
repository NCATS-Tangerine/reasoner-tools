import os
import json
import requests
import sys
import time
import yaml
from greent.flow.dag.tasks import exec_operator
from greent.flow.dag.tasks import calc_dag
from celery import group
from celery.utils.graph import DependencyGraph
from celery.execute import send_task
from types import SimpleNamespace
from celery.result import AsyncResult

def get_workflow(workflow="mq2.yaml"):
    workflow_spec = None
    with open(workflow, "r") as stream:
        workflow_spec = yaml.load (stream.read ())
    return workflow_spec

def call_api(workflow="mq2.yaml"):
    with open(workflow, "r") as stream:
        workflow_spec = yaml.load (stream.read ())
        host = "localhost"
        port = os.environ["ROSETTA_WF_PORT"]
        workflow_spec['args'] = {
            "drug_name" : "imatinib",
            "disease_name" : "asthma"
        }
        response = requests.post (
            f"http://localhost:{port}/api/executeWorkflow",
            json=workflow_spec)
        
        print (f"{json.dumps (response.json (), indent=2)}")

def run_job(j, wf_model, asynchronous=False):
    wf_model.topsort.remove (j)
    print (f"  run: {j}")
    print (f"    sort> {wf_model.topsort}")
    print (f"    done> {wf_model.done.keys()}")
    if asynchronous:
        wf_model.running[j] = exec_operator.delay (model2json(wf_model), j)
    else:
        wf_model.done[j] = exec_operator (model2json(wf_model), j)

def json2model(json):
    return SimpleNamespace (**json)
def model2json(model):
    return {
        "uuid" : model.uuid,
        "spec" : model.spec,
        "inputs" : model.inputs,
        "dependencies" : model.dependencies,
        "topsort" : model.topsort,
        "running" : {},
        "failed" : {},
        "done" : {}
    }

class CeleryDAGExecutor:
    def __init__(self, spec, inputs):
        self.spec = spec
        self.inputs = inputs
    def execute (self, async=False):
        model_dict = calc_dag(self.spec, inputs=self.inputs)
        #print (json.dumps (model_dict, indent=2))
        model = json2model (model_dict)
        total_jobs = len(model.topsort)
        while len(model.topsort) > 0:
            for j in model.topsort:
                print (f"test: {j}")
                if j in model.done:
                    break
                dependencies = model.dependencies[j]
                if len(dependencies) == 0:
                    run_job (j, model, asynchronous=async)
                else:
                    ready = all ([ d in model.done for d in dependencies ])
                    if ready:
                        print (f" t5 ")
                        run_job (j, model, asynchronous=async)
            completed = []
            for job_name, promise in model.running.items ():
                print (f"job {job_name} is ready:{promise.ready()} failed:{promise.failed()}")
                if promise.ready ():
                    completed.append (job_name)
                    model.done[job_name] = promise.get ()
                    sink = model.get("workflow",{}).get(c,{})
                    sink['result'] = model.done[c]
                elif promise.failed ():
                    completed.append (job_name)
                    model.failed[job_name] = promise.get ()
            for c in completed:
                print (f"removing {job_name} from running.")
                del model.running[c]
        #return model
                
if __name__ == '__main__':
    executor = CeleryDAGExecutor (
        spec=get_workflow (),
        inputs={
            "drug_name" : "imatinib",
            "disease_name" : "asthma"
        })
    executor.execute ()
