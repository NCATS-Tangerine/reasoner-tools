"""Flask REST API server for RoboQuery service"""

import argparse
import json
import os
import requests
import logging
import time

from datetime import timedelta
from flask import Flask, jsonify, g, Response, request
from flasgger import Swagger
from greent.servicecontext import ServiceContext
from flask import request
from flask_restful import Resource, reqparse

import builder.api.roboquery_definitions
import builder.api.roboquery_logging_config
from builder.api.roboquery_setup import app, api

class RoboQuery(Resource):
    def post(self):
        """ 
        Initiate a graph query with ROBOKOP Builder and return a Graph with rankings from ROBOKOP Ranker.
        ---
        tags: [RoboQuery]
        parameters:
          - in: body
            name: A machine-readable question graph
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
          time.sleep(3)
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
        ranker_answer = ranker_now_query_response.json()
        return ranker_answer
api.add_resource(RoboQuery, '/')

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