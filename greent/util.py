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
import re

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
    
    @staticmethod
    def load_json (path):
        result = None
        with open (path, 'r') as stream:
            result = json.loads (stream.read ())
        return result

    @staticmethod
    def load_yaml (path):
        result = None
        with open (path, 'r') as stream:
            result = yaml.load (stream.read ())
        return result
    
    def get_resource_obj (resource_name, format=None):
        result = None
        if not format:
            if resource_name.endswith ('.yaml'):
                format = 'yaml'
            else:
                format = 'json'
        path = Resource.get_resource_path (resource_name)
        if os.path.exists (path):
            m = {
                'json' : Resource.load_json,
                'yaml' : Resource.load_yaml
            }
            if format in m:
                result = m[format](path)
        return result

    @staticmethod
    # Modified from:
    # Copyright Ferry Boender, released under the MIT license.
    def deepupdate(target, src, overwrite_keys = [], skip = []):
        """Deep update target dict with src
        For each k,v in src: if k doesn't exist in target, it is deep copied from
        src to target. Otherwise, if v is a list, target[k] is extended with
        src[k]. If v is a set, target[k] is updated with v, If v is a dict,
        recursively deep-update it.

        Updated to deal with yaml structure: if you have a list of yaml dicts,
        want to merge them by "name"

        If there are particular keys you want to overwrite instead of merge, send in overwrite_keys
        """
        if type(src) == dict:
            for k, v in src.items():
                if k in overwrite_keys:
                    target[k] = copy.deepcopy(v)
                elif type(v) == list:
                    if not k in target:
                        target[k] = copy.deepcopy(v)
                    elif type(v[0]) == dict:
                        Resource.deepupdate(target[k],v,overwrite_keys)
                    else:
                        target[k].extend(v)
                elif type(v) == dict:
                    if not k in target:
                        target[k] = copy.deepcopy(v)
                    else:
                        Resource.deepupdate(target[k], v,overwrite_keys)
                elif type(v) == set:
                    if not k in target:
                        target[k] = v.copy()
                    else:
                        target[k].update(v.copy())
                else:
                    if not k in skip:
                        target[k] = copy.copy(v)
        else:
            #src is a list of dicts, target is a list of dicts, want to merge by name (yikes)
            src_elements = { x['name']: x for x in src }
            target_elements = { x['name']: x for x in target }
            for name in src_elements:
                if name in target_elements:
                    Resource.deepupdate(target_elements[name], src_elements[name],overwrite_keys)
                else:
                    target.append( src_elements[name] )

class Curie_Resolver:
    @staticmethod 
    def get_curie_to_uri_map():
        return {
            'BFO': 'http://purl.obolibrary.org/obo/BFO_',
            'CARO': 'http://purl.obolibrary.org/obo/CARO_',
            'CHEBI' : 'http://purl.obolibrary.org/obo/CHEBI_',
            'CL': 'http://purl.obolibrary.org/obo/CL_',
            'COHD' : 'http://purl.obolibrary.org/obo/COHD_',
            'DOID' : 'http://purl.obolibrary.org/obo/DOID_',
            'EFO': 'http://www.ebi.ac.uk/efo/EFO_',
            'GARD': 'http://purl.obolibrary.org/obo/GARD_',
            'GO': 'http://purl.obolibrary.org/obo/GO_',
            'HGNC': 'http://identifiers.org/hgnc/',
            'HP': 'http://purl.obolibrary.org/obo/HP_',
            'ICD9': 'http://purl.obolibrary.org/obo/ICD9_',
            'ICD10': 'http://purl.obolibrary.org/obo/ICD10_',
            'MEDDRA': 'http://identifiers.org/meddra:',
            'MESH': 'http://purl.obolibrary.org/obo/MESH_',
            'MONDO': 'http://purl.obolibrary.org/obo/MONDO_',
            'NCIT' : 'http://purl.obolibrary.org/obo/NCIT_',
            'OMIM': 'https://www.omim.org/entry/',
            'OMIMPS': 'http://purl.obolibrary.org/obo/OMIMPS_',
            'ONCOTREE': 'http://purl.obolibrary.org/obo/ONCOTREE_',
            'ORPHANET': 'http://www.orpha.net/ORDO/Orphanet_',
            'PATO': 'http://purl.obolibrary.org/obo/PATO_',
            'PR': 'http://purl.obolibrary.org/obo/PR_',
            'SCTID': 'http://purl.obolibrary.org/obo/SCTID_',
            'SNOMEDCT': 'http://identifiers.org/snomedct/',
            'UBERON': 'http://purl.obolibrary.org/obo/UBERON_',
            'UMLS': 'http://linkedlifedata.com/resource/umls/id/'
        }

    @staticmethod
    def uri_to_curie(uri):
        """
        Try to find if we can get url in the list else return original uri unchanged
        """
        map = Curie_Resolver.get_curie_to_uri_map()
        for curie in map:
            uri_part = map[curie]
            if uri.startswith(uri_part):
                uri = uri.replace(uri_part, f'{curie}:')
                break
        return uri

    @staticmethod
    def curie_to_uri(curie):        
        curie_prefix = curie.split(':')[0]
        return curie.replace(f'{curie_prefix}:', Curie_Resolver.get_curie_to_uri_map().get(curie_prefix,'Unkown Prefix'))
