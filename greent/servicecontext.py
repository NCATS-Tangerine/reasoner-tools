import os
from greent.cache import Cache
from greent.core import GreenT
from greent.config import Config
from greent.util import LoggingUtil

class ServiceContext:
    """ A context for all service objects. Centralizes control over how services behave
    and a common point of coniguration. """
    
    def __init__(self, config=None):
        if config is None:
            config_name = "greent.conf"
            config = os.path.join (os.path.dirname (__file__), config_name)
        self.config = Config (config)
        self.core = GreenT (self)
        self.cache = Cache ()
        
    @staticmethod
    def create_context (config=None):
        return ServiceContext (config)
    
