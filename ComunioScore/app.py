import logging
import argparse
from ComunioScore.routes.router import Router
from ComunioScore.api import APIHandler
from ComunioScore.restdb import RestDB
from ComunioScore.utils.logger import Logger
from ComunioScore.livedata import LiveDataProvider


class ComunioScore:

    def __init__(self, name):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('create class ComunioScore')

        self.name = name

        # defines the api handler methods
        self.api = APIHandler()

        # router instance for specific endpoints
        self.router = Router(name=self.name)
        self.router.add_endpoint('/', 'index', method="GET", handler=self.api.index)

        # create instance db agent
        restdb = RestDB(config_file='cfg.ini')
        restdb.start()

        # provide livedata
        #live = LiveDataProvider()
        #live.start()

    def run(self, host='0.0.0.0', port=None, debug=None):
        """ runs the ComunioScore application on given port

        :param host: default hostname
        :param port: port for the webserver
        :param debug: debug mode true or false
        """
        self.logger.info("running application on port: {}".format(port))
        self.router.run(host=host, port=port, debug=debug)


def main():

    # parse arguments
    parser = argparse.ArgumentParser(description="Arguments for application ComunioScore")
    parser.add_argument('--host',       type=str, help='hostname for the application')
    parser.add_argument('--port',       type=int, help='port for the application')
    parser.add_argument('--log-folder', type=str, help='log folder for ComunioScore')
    args = parser.parse_args()

    if args.host is None:
        host = '0.0.0.0'
    else:
        host = args.host

    if args.port is None:
        port = 8086
    else:
        port = args.port

    if args.log_folder is None:
        log_folder = '/var/log/'
    else:
        log_folder = args.log_folder

    # set up logger instance
    logger = Logger(name='ComunioScore', level='info', log_folder=log_folder)
    logger.info("start application ComunioScoreApp")

    # create application instance
    cs = ComunioScore(name="ComunioScoreApp")

    # run the application
    cs.run(host=host, port=port)


if __name__ == '__main__':
    main()
