import logging
#import inspect
import json
#import requests
import traceback
import unittest
import datetime
import os
#import yaml
from collections import namedtuple
#from bravado.client import SwaggerClient
#from bravado.requests_client import RequestsClient
import copy

#loggers = {}
class LoggingUtil(object):
    """ Logging utility controlling format and setting initial logging level """
    @staticmethod
    def init_logging (name, level=logging.INFO, format='short'):
        logger = logging.getLogger(__name__)
        if not logger.parent.name == 'root':
            return logger

        FORMAT = {
            "short" : '%(funcName)s: %(message)s',
            "medium" : '%(funcName)s: %(asctime)-15s %(message)s',
            "long"  : '%(asctime)-15s %(filename)s %(funcName)s %(levelname)s: %(message)s'
        }[format]
        handler = logging.StreamHandler()
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)
        logger = logging.getLogger (name)
        logger.addHandler(handler)
        logger.setLevel(level)
        return logger

class Resource:
    @staticmethod
    def get_resource_path(resource_name):
       # Given a string resolve it to a module relative file path unless it is already an absolute path.
        resource_path = resource_name
        if not resource_path.startswith (os.sep):
            resource_path = os.path.join (os.path.dirname (__file__), resource_path)
        return resource_path