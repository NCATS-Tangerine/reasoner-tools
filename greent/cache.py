import json
import logging
import operator
import os
import pickle
import requests
import traceback
from greent.util import LoggingUtil
from lru import LRU

logger = LoggingUtil.init_logging(__name__, level=logging.DEBUG)

class CacheSerializer:
    """ Generic serializer. """
    def __init__(self):
        pass

class PickleCacheSerializer(CacheSerializer):
    """ Use Python's default serialization. """
    def __init__(self):
        pass
    def dumps(self, obj):
        return pickle.dumps (obj)
    def loads(self, str):
        return pickle.loads (str)

class JSONCacheSerializer(CacheSerializer):
    pass # would be nice

class Cache:
    """ Cache objects by configurable means. """
    def __init__(self, cache_path="cache",
                 serializer=PickleCacheSerializer,
                 redis_host="localhost", redis_port=6379, redis_db=0,
                 enabled=True):
        
        """ Connect to cache. """
        self.enabled = enabled
        self.cache = LRU (1000) 
        self.serializer = serializer ()
        
    def get(self, key):
        """ Get a cached item by key. """
        result = None
        if self.enabled:
            if key in self.cache:
                result = self.cache[key]
        return result
    
    def set(self, key, value):
        """ Add an item to the cache. """
        if self.enabled:
            self.cache[key] = value

