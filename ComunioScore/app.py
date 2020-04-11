import logging
import argparse

from ComunioScore.routes.router import Router
from ComunioScore.api import APIHandler
from ComunioScore.dbagent import DBAgent
from ComunioScore.utils.logger import Logger
#from ComunioScore.livedata import LiveDataProvider
from ComunioScore import __version__


class ComunioScore:

    def __init__(self, name, comunio_user, comunio_pass, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('create class ComunioScore')

        self.name = name
        self.comunio_user = comunio_user
        self.comunio_pass = comunio_pass

        # defines the api handler methods
        self.api = APIHandler()

        # router instance for specific endpoints
        self.router = Router(name=self.name)
        self.router.add_endpoint('/', 'index', method="GET", handler=self.api.index)

        # create dbagent instance
        dbagent = DBAgent(comunio_user=self.comunio_user, comunio_pass=self.comunio_pass, **dbparams)

        #restdb = RestDB(config_file='cfg.ini')
        #restdb.start()

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

    # ComuniScore usage
    usage1 = "ComunioScore "
    usage2 = "ComunioScore "

    description = "console script for application ComunioScore \n\nUsage:\n    {}\n    {}".format(usage1, usage2)
    # parse arguments for ComunioScore
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)

    # arguments for the server
    parser.add_argument('-ho', '--host',      type=str, help='hostname for the application')
    parser.add_argument('-po', '--port',      type=int, help='port for the application')

    # arguments  for the database
    parser.add_argument('-H', '--dbhost',     type=str, help='Hostname for the database connection', required=True)
    parser.add_argument('-P', '--dbport',     type=int, help='Port for the database connection',     required=True)
    parser.add_argument('-U', '--dbuser',     type=str, help='User for the database connection',     required=True)
    parser.add_argument('-p', '--dbpassword', type=str, help='Password from the user',               required=True)
    parser.add_argument('-DB', '--dbname',    type=str, help='Database name',                        required=True)

    # arguments for comunio login
    parser.add_argument('-cu', '--comunio_user', type=str, help='User for the comunio login',        required=True)
    parser.add_argument('-cp', '--comunio_pass', type=str, help='Password for the comunio login',    required=True)

    # argument for the log folder
    parser.add_argument('-l', '--log-folder',  type=str, help='log folder for ComunioScore Application')

    # argument for the current version
    parser.add_argument('-v', '--version', action='version', version=__version__, help='show the current version')

    # parse all arguments
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

    dbparams = dict()
    dbhost = args.dbhost
    dbport = args.dbport
    dbusername = args.dbuser
    dbpassword = args.dbpassword
    dbname = args.dbname
    dbparams.update({'host': dbhost, 'port': dbport, 'username': dbusername, 'password': dbpassword,
                                     'dbname': dbname})

    comunio_user = args.comunio_user
    comunio_pass = args.comunio_pass

    # set up logger instance
    logger = Logger(name='ComunioScore', level='info', log_folder=log_folder)
    logger.info("start application ComunioScore")

    # create application instance
    cs = ComunioScore(name="ComunioScore", comunio_user=comunio_user, comunio_pass=comunio_pass, **dbparams)

    # run the application
    cs.run(host=host, port=port)


if __name__ == '__main__':
    main()
