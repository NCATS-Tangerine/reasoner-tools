import re
import requests
from greent.service import Service
from greent.cache import Cache

class CachedService(Service):
    """ A service that caches requests. """
    def __init__(self, name, context):
        super(CachedService,self).__init__(name, context)
        self.punctuation = re.compile('[ ?=\./:{}]+')
    
    def get(self, url, params=None, headers=None):
        key = self.punctuation.sub ('', url)
        obj = self.context.cache.get(key)
        if not obj:
            if params==None and headers==None:
                obj = requests.get(url).json()
            elif params and headers:
                obj = requests.get(url, params=params, headers=headers).json()
            elif params and headers==None: # pragma: no cover
                obj = requests.get(url, params=params).json()
            elif params==None and headers: # pragma: no cover
                obj = requests.get(url, headers=headers).json()
            self.context.cache.set(key, obj)
        return obj

