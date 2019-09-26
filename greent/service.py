import os
from greent.util import LoggingUtil
from datetime import datetime as dt

class Service:
    """ Basic characteristics of services. """

    def __init__(self, name, context):
        """ Initialize the service given a name and an application context. """
        self.context = context
        self.name = name
        self.url = context.config.get_service (self.name).get("url", None)
        try:
            self.concept_model = getattr(context, 'rosetta-graph').concept_model
        except:
            pass
        setattr (self.context, self.name, self)

    def _type(self):
        return self.__class__.__name__

    def get_config(self):
        result = {}
        try:
            result = self.context.config.get_service (self.name)
        except:
            logger = LoggingUtil.init_logging(__name__)
            logger.warn(f"Unable to get config for service: {self.name}")
        return result

    def __str__():
        return f"Service name={self.name}\n, url={self.url}"
