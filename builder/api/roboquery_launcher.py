"""Flask REST API server for RoboQuery service"""

import argparse
import json
import os
import requests

from flask import Flask, jsonify, g, Response
from flasgger import Swagger
from greent.servicecontext import ServiceContext
from flask import request
from flask_restful import Resource, reqparse

import builder.api.roboquery_definitions

from builder.api.roboquery_setup import app, api

class RoboQuery(Resource):
    def post(self):
        """ 
        Initiate a graph query with ROBOKOP Builder and return a Graph with rankings from ROBOKOP Ranker.
        ---
        tags: [RoboQuery]
        parameters:
          - in: body
            name: question
            description: The machine-readable question graph.
            schema:
                $ref: '#/definitions/Question'
            required: true
        responses:
            202:
                description: Update started...
                schema:
                    type: object
                    required:
                      - task id
                    properties:
                        task id:
                            type: string
                            description: task ID to poll for KG update status
        """
        # replace `parameters`` with this when OAS 3.0 is fully supported by Swagger UI
        # https://github.com/swagger-api/swagger-ui/issues/3641
        """
        requestBody:
            description: The machine-readable question graph.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Question'
        """
        logger = logging.getLogger('builder')
        logger.info("Queueing 'KG update' task...")
        task = update_kg.apply_async(args=[request.json])
        return {'task id': task.id}, 202

api.add_resource(RoboQuery, '/')


# @app.route('/api/builder_query/<curie>/<curie_name>')
# def builder_query (curie, curie_name):
#    """ 
#    Initiate a graph query with ROBOKOP Builder and return a Graph with rankings from ROBOKOP Ranker.
#    ---
#    tags: [RoboQuery]
#    parameters:
#      - name: curie
#        in: path
#        type: string
#        required: true
#        default: MONDO:0005737
#        description: "Enter an ontological ID."
#        x-valueType:
#          - http://schema.org/string
#        x-requestTemplate:
#          - valueType: http://schema.org/string
#            template: /builder_query_curie/{{ input }}/{{ input2 }}
     
#      - name: curie_name
#        in: path
#        type: string
#        required: true
#        default: Ebola hemorrhagic fever
#        description: "Enter a corresponding name."
#        x-valueType:
#          - http://schema.org/string
#        x-requestTemplate:
#          - valueType: http://schema.org/string
#            template: /builder_query_curie_name/{{ input }}/{{ input2 }}
#    responses:
#      200:
#        description: ...
#    """
#    assert curie, "A string must be entered as a query."
#    assert curie_name, "A string..."
#    builder_query_1_url = "http://127.0.0.1:6010/api/"
#    builder_query_1_headers = {
#      'accept' : 'application/json',
#      'Content-Type' : 'application/json' 
#    }
#    builder_query_1_data = {
#             "machine_question": {
#               "edges": [
#                 {
#                   "source_id": 0,
#                   "target_id": 1
#                 },
#                 {
#                   "source_id": 1,
#                   "target_id": 2
#                 }
#               ],
#               "nodes": [
#                 {
#                   "curie": curie,
#                   "id": 0,
#                   "name": curie_name,
#                   "type": "disease"
#                 },
#                 {
#                   "id": 1,
#                   "type": "gene"
#                 },
#                 {
#                   "id": 2,
#                   "type": "genetic_condition"
#                 }
#               ]
#             }
#           }
#    builder_query_1_response = requests.post(builder_query_1_url, \
#     headers = builder_query_1_headers, json = builder_query_1_data)
#    builder_task_id_string = builder_query_1_response.json()
#    return json.dumps(builder_task_id_string)

# @app.route('/api/builder_status_check/<task_id>')
# def builder_status_check (task_id):
#    """ Use the Task ID from Step 1 to check on the graph process.
#    ---
#    parameters:
#      - name: task_id
#        in: path
#        type: string
#        required: true
#        default:
#        description: "Enter a task ID from Builder Step 1."
#        x-valueType:
#          - http://schema.org/string
#        x-requestTemplate:
#          - valueType: http://schema.org/string
#            template: /builder_query_task_id/{{ input }}/{{ input2 }} 
#    responses:
#      200:
#        description: ...
#    """
#    assert builder_task_id, "A string."
#    builder_task_status_url = "http://127.0.0.1:6010/api/task/"+builder_task_id
#    builder_task_status_response = requests.get(builder_task_status_url)
#    builder_status = builder_query_2_response.json()
#    return json.dumps(builder_status)

# @app.route('/api/ranker_query/<curie>/<curie_name>')
# def query_to_robo_ranker (curie, curie_name):
#    """ Initiate a graph ranking process with ROBOKOP Ranker and return the task id
#    ---
#    parameters:
#      - name: curie
#        in: path
#        type: string
#        required: true
#        default: MONDO:0005735
#        description: "Enter an Ontological ID."
#        x-valueType:
#          - http://schema.org/string
#        x-requestTemplate:
#          - valueType: http://schema.org/string
#            template: /ranker_query_curie/{{ input }}/{{ input2 }}
#      - name: curie_name
#        in: path
#        type: string
#        required: true
#        default: Ebola hemorrhagic fever
#        description: "Enter a corresponding name."
#        x-valueType:
#          - http://schema.org/string
#        x-requestTemplate:
#          - valueType: http://schema.org/string
#            template: /ranker_query_curie_name/{{ input }}/{{ input2 }}  
#    responses:
#      200:
#        description: ...
#    """
#    assert curie, "A string must be entered as a query."
#    assert curie_name, "A string..."
#    ranker_query_1_url = "http://127.0.0.1:6011/api/"
#    ranker_query_1_headers = {
#      'accept' : 'application/json',
#      'Content-Type' : 'application/json' 
#    }
#    ranker_query_1_data = {
#             "machine_question": {
#               "edges": [
#                 {
#                   "source_id": 0,
#                   "target_id": 1,
#                   "type": "disease_to_gene_association"
#                 },
#                 {
#                   "source_id": 1,
#                   "target_id": 2,
#                   "type": "has_phenotype"
#                 }
#               ],
#               "nodes": [
#                 {
#                   "curie": curie,
#                   "id": 0,
#                   "type": "disease"
#                 },
#                 {
#                   "id": 1,
#                   "type": "gene"
#                 },
#                 {
#                   "id": 2,
#                   "type": "genetic_condition"
#                 }
#               ]
#             }
#           }
#    ranker_query_1_response = requests.post(ranker_query_1_url, \
#     headers = ranker_query_1_headers, json = ranker_query_1_data)
#    ranker_task_id_string = ranker_query_1_response.json()
#    return json.dumps(ranker_task_id_string)

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Robo_query_to_graph Server')
   parser.add_argument('-p', '--port',  type=int, help='Port to run service on.', default=5000)
   parser.add_argument('-d', '--debug', help="Debug.", default=False)
   parser.add_argument('-c', '--conf',  help='GreenT config file to use.', default="greent.conf")
   args = parser.parse_args ()
   app.config['SWAGGER']['greent_conf'] = args.greent_conf = args.conf
   app.config['robo_query_to_graph'] = {
       'config' : args.conf,
       'debug'  : args.debug
   }
   app.run(host='0.0.0.0', port=args.port, debug=True, threaded=True)