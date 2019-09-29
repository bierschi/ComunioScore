import json
from flask import Response, request
#from ComunioScore.db.fetcher import DBFetcher


class APIHandler:
    """ class APIHandler to link routes to specific handler function

    USAGE:
            api = APIHandler(host=host, port=port, username=username, password=password, dbname=dbname)

    """
    def __init__(self):
        """
                self.db = DBFetcher()
        try:
            self.db.connect(host=host, port=port, username=username, password=password, dbname=dbname, minConn=1, maxConn=5)
        except Exception as e:
            print(e)


        """

    def index(self):
        """

        :return:
        """
        return "hello world"

