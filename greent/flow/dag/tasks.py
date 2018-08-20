from __future__ import absolute_import
import json
import time
import greent.flow.dag.conf as Conf
from greent.flow.dag.celery_app import app
from greent.flow.rosetta_wf import Workflow

@app.task(bind=True, queue="rosetta")
def longtime_add(self, x, y):
    print ('long time task begins')
    # sleep 5 seconds
    time.sleep(5)
    print ('long time task finished')
    return x + y


@app.task(bind=True, queue="rostta")
def execute_workflow (self, inputs, workflow_spec):
    workflow = Workflow (
        inputs = inputs,
        spec = workflow_spec)
    return workflow.execute ()
