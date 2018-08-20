#!/usr/bin/env python

""" Flask REST API server """

import os
import logging
import json
import redis
from datetime import datetime
from flask_restful import Resource
from flask import request
from greent.flow.dag.api_setup import api, app
from greent.flow.dag.tasks import execute_workflow

logger = logging.getLogger("rosetta")

class ExecuteWorkflow(Resource):
    def post(self):
        """
        ExecuteWorkflow
        ---
        tags: [executeWorkflow]
        summary: "Execute a Rosetta workflow."
        description: ""
        operationId: "executeWorkflow"
        consumes:
          - "application/json"
        produces:
          - "application/json"
        parameters:
          - in: "body"
            name: "body"
            description: "Workflow to be executed"
            required: true
            #schema:
            #    $ref: "#/definitions/Query"
        responses:
            200:
                description: "successful operation"
                #schema:
                #    $ref: "#/definitions/Response"
            400:
                description: "Invalid status value"
        """
        workflow_spec = request.json
        
        logger.debug(f"Received request {workflow_spec}.")        
        print (f"Received request {json.dumps(workflow_spec,indent=2)}.")

        response = execute_workflow (
            inputs={"drug_name" : "imatinib"},
            workflow_spec=workflow_spec)

        return response, 200

api.add_resource(ExecuteWorkflow, '/executeWorkflow')

if __name__ == '__main__':

    # Get host and port from environmental variables
    
    server_host = '0.0.0.0'
    server_port = int(os.environ['ROSETTA_WF_PORT'])

    app.run(host=server_host,\
        port=server_port,\
        debug=False,\
        use_reloader=True)
