'''
Set up Flask server
'''

from flask import Flask, Blueprint
from flask_restful import Api
from flasgger import Swagger

app = Flask(__name__, static_folder='../pack', template_folder='../templates')

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_blueprint)
app.register_blueprint(api_blueprint)

template = {
    "openapi": "2.0", #3.0.1",
    "info": {
        "title": "ROBOKOP Graph Building and Ranking API",
        "description": "Generic API to turn small machine-readable queries into large, enriched, and ranked knowledge graphs",
        "contact": {
            "responsibleOrganization": "Renaissance Computing Institute",
            "responsibleDeveloper": "ckcurtis@renci.com",
            "email": "ckcurtis@renci.org",
            "url": "www.renci.org",
        },
        "termsOfService": "<url>",
        "version": "0.0.3"
    },
    "schemes": [
        "http",
        "https"
    ]
}
app.config['SWAGGER'] = {
    'title': 'RoboQuery',
    'uiversion': 3
}
swagger = Swagger(app, template=template)
