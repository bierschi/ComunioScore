import logging
from ComunioScore.routes.router import Router
from ComunioScore.api import APIHandler
from ComunioScore.dbagent import DBAgent
from ComunioScore.utils.logger import Logger


class ComunioScore:

    def __init__(self, name):
        self.logger = logging.getLogger('ComunioScoreApp')
        self.logger.info('create class ComunioScore')

        self.name = name

        # defines the api handler methods
        self.api = APIHandler()

        # router instance for specific endpoints
        self.router = Router(name=self.name)
        self.router.add_endpoint('/', 'index', method="GET", handler=self.api.index)

        # create instance db agent
        dbagent = DBAgent(config_file='cfg.ini')
        dbagent.start()

    def run(self, host='0.0.0.0', port=None, debug=None):
        """ runs the ComunioScore application on given port

        :param host: default hostname
        :param port: port for the webserver
        :param debug: debug mode true or false
        """
        self.logger.info("running application on port: {}".format(port))
        self.router.run(host=host, port=port, debug=debug)


def main():
    # set up logger instance
    logger = Logger(name='ComunioScoreApp', level='info', log_folder='var/log/', debug=True)
    logger.info("start application ComunioScoreApp")

    # create application instance
    cs = ComunioScore(name="ComunioScoreApp")

    # run the application
    cs.run(host='0.0.0.0', port=8086)


if __name__ == '__main__':
    main()
