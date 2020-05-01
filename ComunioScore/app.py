import logging
import argparse
import configparser
from configparser import NoOptionError, NoSectionError

from ComunioScore.routes import Router
from ComunioScore import APIHandler, ComunioDB, SofascoreDB
from ComunioScore.utils import Logger
from ComunioScore.livedata import LiveData
from ComunioScore.matchscheduler import MatchScheduler
from ComunioScore.messenger import ComunioScoreTelegram
from ComunioScore import __version__


class ComunioScore:
    """ class ComunioScore to setup all instances and register event handler for the application

    USAGE:
            cs = ComunioScore(name="ComunioScore", comunio_user=comunio_user, comunio_pass=comunio_pass, token=token,
            season_date=season_date, **dbparams)
            cs.run(host=host, port=port)

    """
    def __init__(self, name, comunio_user, comunio_pass, token, season_date, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class ComunioScore')

        self.name = name
        self.comunio_user = comunio_user
        self.comunio_pass = comunio_pass
        self.token = token
        self.season_date = season_date

        # defines the api handler methods
        self.api = APIHandler()

        # router instance for specific endpoints
        self.router = Router(name=self.name)
        self.router.add_endpoint('/', 'index', method="GET", handler=self.api.index)

        # create telegram instance
        self.telegram = ComunioScoreTelegram(token=self.token)

        # create ComunioDB instance
        self.comuniodb = ComunioDB(comunio_user=self.comunio_user, comunio_pass=self.comunio_pass, **dbparams)

        # create LiveData instance
        self.livedata = LiveData(season_date=self.season_date, token=self.token, **dbparams)
        self.livedata.register_update_squad_event_handler(func=self.comuniodb.update_linedup_squad)
        self.livedata.register_telegram_send_event_handler(func=self.telegram.new_msg)

        # register summery points, rate and cancel event handler
        self.telegram.register_points_summery_event_handler(func=self.livedata.points_summery)
        self.telegram.register_rate_event_handler(func=self.livedata.set_msg_rate)
        self.telegram.register_cancel_event_handler(func=self.livedata.set_notify_flag)

        # create MatchScheduler instance
        self.matchscheduler = MatchScheduler()
        self.matchscheduler.register_livedata_event_handler(func=self.livedata.fetch)

        # create SofascoreDB instance
        self.sofascoredb = SofascoreDB(season_date=self.season_date, **dbparams)
        self.sofascoredb.register_matchscheduler_event_handler(func=self.matchscheduler.new_event)
        self.sofascoredb.register_comunio_user_data(func=self.comuniodb.get_comunio_user_data)

    def run(self, host='0.0.0.0', port=None, debug=None):
        """ runs the ComunioScore application on given port

        :param host: default hostname
        :param port: port for the webserver
        :param debug: debug mode true or false
        """
        # start comuniodb run thread
        self.comuniodb.start()
        # start sofascoredb run thread
        self.sofascoredb.start()
        # start telegram polling
        self.telegram.run()
        self.logger.info("running application on port: {}".format(port))
        self.router.run(host=host, port=port, debug=debug)


def main():

    # ComuniScore usage
    usage1 = "ComunioScore args --host 127.0.0.1 --port 8086 --dbhost 127.0.01 --dbport 5432 --dbuser john " \
             "--dbpassword jane --dbname comunioscore --comunio_user john --comunio_pass jane --token adfefad"

    usage2 = "ComunioScore config --file /etc/comunioscore/comunioscore.ini"

    description = "console script for application ComunioScore \n\nUsage:\n    {}\n    {}".format(usage1, usage2)

    # parse arguments for ComunioScore
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)

    subparser = parser.add_subparsers(dest='parseoption', help='Choose the option between pure arguments (args) '
                                                               'or a configuration (config) file')

    config_parser = subparser.add_parser('config', help='Define a configuration file')
    args_parser   = subparser.add_parser('args', help='Use pure command line arguments')

    # argument for the configfile
    config_parser.add_argument('-f', '--file', type=str, help='Path to the configuration file')

    # arguments for the server
    args_parser.add_argument('-ho', '--host',      type=str, help='hostname for the application')
    args_parser.add_argument('-po', '--port',      type=int, help='port for the application')

    # arguments  for the database
    args_parser.add_argument('-H', '--dbhost',     type=str, help='Hostname for the database connection', required=True)
    args_parser.add_argument('-P', '--dbport',     type=int, help='Port for the database connection',     required=True)
    args_parser.add_argument('-U', '--dbuser',     type=str, help='User for the database connection',     required=True)
    args_parser.add_argument('-p', '--dbpassword', type=str, help='Password from the user',               required=True)
    args_parser.add_argument('-DB', '--dbname',    type=str, help='Database name',                        required=True)

    # arguments for comunio login
    args_parser.add_argument('-cu', '--comunio_user', type=str, help='User for the comunio login',        required=True)
    args_parser.add_argument('-cp', '--comunio_pass', type=str, help='Password for the comunio login',    required=True)

    args_parser.add_argument('-t', '--token', type=str, help='Telegram token')

    # argument for the current version
    parser.add_argument('-v', '--version', action='version', version=__version__, help='show the current version')

    # parse all arguments
    args = parser.parse_args()

    dbparams = dict()

    # parse config file
    if args.parseoption == 'config':
        configfile = args.file

        config = configparser.ConfigParser()
        config.read(configfile)

        try:

            # comunio section
            comunio_user = config.get('comunio', 'username')
            comunio_pass = config.get('comunio', 'password')

            # database section
            dbhost     = config.get('database', 'host')
            dbport     = config.getint('database', 'port')
            dbusername = config.get('database', 'username')
            dbpassword = config.get('database', 'password')
            dbname     = config.get('database', 'dbname')

            # server section
            host = config.get('server', 'host')
            port = config.getint('server', 'port')

            # telegram section
            token = config.get('telegram', 'token')
            season_date = config.get('season', 'startdate')

        except (NoOptionError, NoSectionError) as ex:
            print(ex)
            exit(1)
    else:
        # parse command line arguments
        if args.host is None:
            host = '0.0.0.0'
        else:
            host = args.host

        if args.port is None:
            port = 8086
        else:
            port = args.port

        dbhost = args.dbhost
        dbport = args.dbport
        dbusername = args.dbuser
        dbpassword = args.dbpassword
        dbname = args.dbname

        comunio_user = args.comunio_user
        comunio_pass = args.comunio_pass

        token = args.token

    dbparams.update({'host': dbhost, 'port': dbport, 'username': dbusername, 'password': dbpassword,
                     'dbname': dbname})

    # set up logger instance
    logger = Logger(name='ComunioScore', level='info', log_folder='/var/log/')
    logger.info("Start application ComunioScore")

    # create application instance
    cs = ComunioScore(name="ComunioScore", comunio_user=comunio_user, comunio_pass=comunio_pass, token=token, season_date=season_date, **dbparams)

    # run the application
    cs.run(host=host, port=port)


if __name__ == '__main__':
    main()
