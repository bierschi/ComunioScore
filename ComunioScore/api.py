import json
import logging
from flask import Response, request


class APIHandler:
    """ class APIHandler to link routes to specific handler function

    USAGE:
            api = APIHandler()

    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class APIHandler')

    def index(self):
        """

        :return:
        """
        return "hello world"

