"""Flask REST API server for RoboQuery service"""

import argparse
import json
import os
import requests
import logging
import time
import jsonpath_rw
from datetime import timedelta
from flask import Flask, jsonify, g, Response, request
from flasgger import Swagger
from greent.servicecontext import ServiceContext
from flask import request
from flask_restful import Resource, reqparse
import builder.api.roboquery_definitions
import builder.api.roboquery_logging_config
from builder.api.roboquery_setup import app, api

logger = logging.getLogger("roboquery")

class BuildAndRankOneQuestion(Resource):
    def __init__(self, ranker_answer = {}):
        self.ranker_answer = ranker_answer
        return
        
    def post(self, ranker_answer={}):
        """ 
        Initiate a graph query with ROBOKOP Builder and return a Graph with rankings from ROBOKOP Ranker.
        ---
        tags: [RoboQuery]
        parameters:
          - in: body
            name: ok
            description: A machine-readable question graph, entered here, will build
                onto the Knowledge Graph (KG) and return a portion of that KG with rank values.
            schema:
                $ref: '#/definitions/Question'
            required: true
        responses:
            200:
                description: successful operation
            202:
                description: Building onto KG and Ranking results
            400:
                description: Invalid input value(s)    
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
        # First we queue an update to the Knowledge Graph (KG) using ROBOKOP builder
        logger = logging.getLogger('builder KG update task')
        logger.info("Queueing 'KG update' task...")
        
        builder_query_1_url = "http://127.0.0.1:6010/api/"
        builder_query_1_headers = {
          'accept' : 'application/json',
          'Content-Type' : 'application/json'
          }
        print(request.json)
        builder_query_1_data = request.json
        builder_query_1_response = requests.post(builder_query_1_url, \
          headers = builder_query_1_headers, json = builder_query_1_data)
        builder_task_id = builder_query_1_response.json()
        builder_task_id_string = builder_task_id["task id"]

        #now query ROBOKOP Builder for the status of Knowledge Graph work
        logger = logging.getLogger('builder KG update status query')
        logger.info("Checking status of 'KG update' task...")
        
        break_loop = False
        while not break_loop:
          time.sleep(1)
          builder_task_status_url = "http://127.0.0.1:6010/api/task/"+builder_task_id_string
          builder_task_status_response = requests.get(builder_task_status_url)
          builder_status = builder_task_status_response.json()
          if builder_status['status'] == 'SUCCESS':
            break_loop = True
         
        #KG has been updated by Builder, get answers NOW from ROBOKOP Ranker!
        logger = logging.getLogger('Ranker Answer query')
        logger.info("Getting Answers about KG from Ranker...")

        ranker_now_query_url = "http://127.0.0.1:6011/api/now"
        ranker_now_query_headers = {
          'accept' : 'application/json',
          'Content-Type' : 'application/json'
          }
        ranker_now_query_data = request.json
        ranker_now_query_response = requests.post(ranker_now_query_url, \
          headers = builder_query_1_headers, json = builder_query_1_data)
        self.ranker_answer = ranker_now_query_response.json()
        #print(self.ranker_answer)
        return self.ranker_answer        

api.add_resource(BuildAndRankOneQuestion, '/one_question')

class ExpandedStartNodes(Resource):
    def __init__(self, ranker_answer = {}):
        self.ranker_answer = ranker_answer
        return
        
    def post(self, ranker_answer={}):
        """ 
        Begin with a MQ, expand the scope of the starting nodes, send to a Reasoner and return an answer set.
        ---
        tags: [RoboQuery]
        parameters:
          - in: body
            name: ok
            description: A machine-readable question graph, entered here, will build
                onto the Knowledge Graph (KG) and return a portion of that KG with rank values.
            schema:
                $ref: '#/definitions/Question'
            required: true
        responses:
            200:
                description: successful operation
            202:
                description: Building onto KG and Ranking results
            400:
                description: Invalid input value(s)    
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
        # First we queue an update to the Knowledge Graph (KG) using ROBOKOP builder
        logger = logging.getLogger('builder KG update task')
        logger.info("Queueing 'KG update' task...")
        
       

        start_name = request.json['machine_question']['nodes'][0]['name']
        start_type = request.json['machine_question']['nodes'][0]
        print(start_type)
        
        #now we need to query bionames.




        # builder_query_1_url = "http://127.0.0.1:6010/api/"
        # builder_query_1_headers = {
        #   'accept' : 'application/json',
        #   'Content-Type' : 'application/json'
        #   }
        # print(request.json)
        # builder_query_1_data = request.json
        # builder_query_1_response = requests.post(builder_query_1_url, \
        #   headers = builder_query_1_headers, json = builder_query_1_data)
        # builder_task_id = builder_query_1_response.json()
        # builder_task_id_string = builder_task_id["task id"]

        #now query ROBOKOP Builder for the status of Knowledge Graph work
        logger = logging.getLogger('builder KG update status query')
        logger.info("Checking status of 'KG update' task...")
        
        # break_loop = False
        # while not break_loop:
        #   time.sleep(1)
        #   builder_task_status_url = "http://127.0.0.1:6010/api/task/"+builder_task_id_string
        #   builder_task_status_response = requests.get(builder_task_status_url)
        #   builder_status = builder_task_status_response.json()
        #   if builder_status['status'] == 'SUCCESS':
        #     break_loop = True
         
        # #KG has been updated by Builder, get answers NOW from ROBOKOP Ranker!
        # logger = logging.getLogger('Ranker Answer query')
        # logger.info("Getting Answers about KG from Ranker...")

        # ranker_now_query_url = "http://127.0.0.1:6011/api/now"
        # ranker_now_query_headers = {
        #   'accept' : 'application/json',
        #   'Content-Type' : 'application/json'
        #   }
        # ranker_now_query_data = request.json
        # ranker_now_query_response = requests.post(ranker_now_query_url, \
        #   headers = builder_query_1_headers, json = builder_query_1_data)
        # self.ranker_answer = ranker_now_query_response.json()
        # #print(self.ranker_answer)
        # return self.ranker_answer        
        return

api.add_resource(ExpandedStartNodes, '/expandedStartNodes')


class BuildAndRankMultipleQuestions(Resource):
    def __init__(self, ranker_answer = {}):
        self.ranker_answer = ranker_answer
        return
        
    def post(self, ranker_answer={}):
        """ 
        Complete sequential Knowledge Graph(KG) queries with a Reasoner and return a KG.
        ---
        tags: [RoboQuery]
        parameters:
          - in: body
            name: build & rank
            description: A machine-readable question graph, entered here, will build
                onto the Knowledge Graph (KG) and return a portion of that KG with rank values.
            schema:
                $ref: '#/definitions/N_Machine_Questions'
            required: true
        responses:
            200:
                description: successful operation
            202:
                description: Building onto KG and Ranking results
            400:
                description: Invalid input value(s)
                     
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
        # First we queue an update to the Knowledge Graph (KG) using ROBOKOP builder
        logger = logging.getLogger('builder KG update task')
        logger.info("Queueing 'KG update' task...")
        
        builder_query_1_url = "http://127.0.0.1:6010/api/"
        builder_query_1_headers = {
          'accept' : 'application/json',
          'Content-Type' : 'application/json'
          }
        builder_query_1_data = request.json
        builder_query_1_response = requests.post(builder_query_1_url, \
          headers = builder_query_1_headers, json = builder_query_1_data)
        builder_task_id = builder_query_1_response.json()
        builder_task_id_string = builder_task_id["task id"]

        #now query ROBOKOP Builder for the status of Knowledge Graph work
        logger = logging.getLogger('builder KG update status query')
        logger.info("Checking status of 'KG update' task...")
        
        break_loop = False
        while not break_loop:
          time.sleep(2)
          builder_task_status_url = "http://127.0.0.1:6010/api/task/"+builder_task_id_string
          builder_task_status_response = requests.get(builder_task_status_url)
          builder_status = builder_task_status_response.json()
          if builder_status['status'] == 'SUCCESS':
            break_loop = True

        #KG has been updated by Builder, get answers NOW from ROBOKOP Ranker!
        logger = logging.getLogger('Ranker Answer query')
        logger.info("Getting Answers about KG from Ranker...")

        ranker_now_query_url = "http://127.0.0.1:6011/api/now"
        ranker_now_query_headers = {
          'accept' : 'application/json',
          'Content-Type' : 'application/json'
          }
        ranker_now_query_data = request.json
        ranker_now_query_response = requests.post(ranker_now_query_url, \
          headers = builder_query_1_headers, json = builder_query_1_data)
        self.ranker_answer = ranker_now_query_response.json()
        #print(self.ranker_answer)
        return self.ranker_answer        

api.add_resource(BuildAndRankMultipleQuestions, '/multiple_questions')

if __name__ == '__main__':

    # Get host and port from environmental variables
    server_host = '0.0.0.0' #os.environ['ROBOQUERY_HOST']
    server_port = int(os.environ['ROBOQUERY_PORT'])

    app.run(host=server_host,\
        port=server_port,\
        debug=False,\
        use_reloader=True)

# class GenerateMachineQuestion(Resource):
#     def __init__(self):
        
#         return
        
#     def post(self):
#         """ 
#         Input search terms to automatically generate a machine-readable question graph.
#         ---
#         tags: [RoboQuery]
#         parameters:
#             - name: test
#               in: body
#               type: string
#               required: true
#               default: imatinib
#               description: A biologically or medically impactful name or idea.
             
#         responses:
#             200:
#                 description: ...
        
#         requestBody:
#             description: test
#             required: true
#             content:
#                 application/json:
#         """        

#         print(request.get_data())
#         print(request.get_json())
#         print(request.stream.read())
#         return

# api.add_resource(GenerateMachineQuestion, '/generate_machine_question/')

# class Refine(Resource):
#     def __init__(self):
#         self.test = BuildAndRank()
    
#     def post(self):
#         """ 
#         Refining our previous KG response and performing a new reasoning operation...
#         ---
#         tags: [RoboQuery]
#         parameters:
#           - in: body
#             name: refine
#             description: The output of the previous Build & Rank operation is utilized, with or without
#                 revision, to get back a more-refined Knowledge Graph.
#             schema:
#                 $ref: '#/definitions/Question'
#             required: true
#         responses:
#             200:
#                 description: successful operation
#             400:
#                 description: Invalid input value(s)
#         """
#         return

# api.add_resource(Refine, '/refine')