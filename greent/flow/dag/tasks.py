from __future__ import absolute_import
import json
import time
import greent.flow.dag.conf as Conf
#import networkx as nx
#import uuid
#from networkx.algorithms import lexicographical_topological_sort
from greent.flow.dag.celery_app import app
from greent.flow.rosetta_wf import Workflow
from greent.flow.rosetta_wf import Router
#from celery.utils.graph import DependencyGraph
#from celery import group

def json2model(json):
    model = Workflow (spec={ "a" : "b"})
    model.uuid = json['uuid']
    model.spec = json['spec']
    model.inputs = json['inputs']
    model.dependencies = json['dependencies']
    model.topsort = json['topsort']
    model.running = json['running']
    model.failed = json['failed']
    model.done = json['done']
    return model

@app.task(bind=True, queue="rosetta")
def calc_dag (self, workflow_spec, inputs):
    return Workflow (workflow_spec, inputs=inputs).json ()

@app.task(bind=True, queue="rosetta")
def exec_operator(self, model, job_name):
    result = None
    wf = json2model (model)
    op_node = wf.spec.get("workflow",{}).get(job_name,{})
    if op_node:
        router = Router (wf)
        result = router.route (wf, op_node, job_name, op_node['code'], op_node['args'])
        wf.set_result (job_name, result)
    return result
