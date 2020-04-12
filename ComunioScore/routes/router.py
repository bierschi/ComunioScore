import logging
from flask import Flask


class Router:
    """ class Router to add multiple endpoints to the flask application

    USAGE:
            routes = Router(name="TestApp")
            routes.add_endpoint(endpoint='/', endpoint_name="index", method="GET", handler=<function>)
            routes.run()
    """

    def __init__(self, name):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class Router')

        self.name = name
        self.app = Flask(self.name)

    def run(self, host='0.0.0.0', port=None, debug=None):
        """ runs the development flask server

        :param host: default hostname
        :param port: the port of the webserver
        :param debug: run with debug output
        """
        self.app.run(host=host, port=port, debug=debug)

    def add_endpoint(self, endpoint=None, endpoint_name=None, method=None, handler=None):
        """ adds an endpoint to the application

        :param endpoint: specific endpoint for the app
        :param endpoint_name: endpoint name for the app
        :param method: method for handler call (POST, PUT, DELETE, GET)
        :param handler: handler function/method to execute
        """
        if method == "POST":
            self.app.add_url_rule(endpoint, endpoint_name, handler, methods=["POST"])
        elif method == "PUT":
            self.app.add_url_rule(endpoint, endpoint_name, handler, methods=["PUT"])
        elif method == "DELETE":
            self.app.add_url_rule(endpoint, endpoint_name, handler, methods=["DELETE"])
        else:
            self.app.add_url_rule(endpoint, endpoint_name, handler)
