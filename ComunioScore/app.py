import configparser
from ComunioScore.routes.router import Router
from ComunioScore.api import APIHandler
from ComunioScore.dbagent import DBAgent
from ComunioScore import ROOT_DIR

#config = configparser.ConfigParser()
#config.read(ROOT_DIR + '/config/cfg.ini')


class ComunioScore:

    def __init__(self, name):
        self.name = name

        # defines the api handler methods
        self.api = APIHandler()

        # router instance for specific endpoints
        self.router = Router(name=self.name)
        self.router.add_endpoint('/', 'index', method="GET", handler=self.api.index)

        # create instance db agent
        dbagent = DBAgent(config_file='cfg.ini')
        dbagent.start()

    def run(self, port=None, debug=None):
        """ runs the ComunioScore application on given port

        :param port: port for the webserver
        :param debug: debug mode true or false
        """

        self.router.run(port=port, debug=debug)


def main():

    # create application instance
    cs = ComunioScore(name="ComunioScoreApp")

    # run the application
    cs.run()


if __name__ == '__main__':
    main()
