import logging
import configparser
from ComunioScore.db.connector import DBConnector
from ComunioScore.db.inserter import DBInserter
from ComunioScore.db.fetcher import DBFetcher
from ComunioScore.db.creator import DBCreator, Schema, Table, Column
from ComunioScore import ROOT_DIR


class DBAgent:
    """ Base class DBAgent which provides database actions for subclasses

    USAGE:
            dbagent = DBAgent()

    """
    def __init__(self, config_file):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('create class DBAgent')

        # create configparser
        self.config_file = config_file
        self.config = configparser.ConfigParser()

        # try first ini file in config folder
        self.config.read(ROOT_DIR + '/config/' + config_file)
        try:
            # check if keys are readable
            self.comunioscore_schema = self.config.get('comunioscore', 'schema')
        except (KeyError, configparser.NoSectionError) as e:
            self.logger.error("failed to load config file. Try to use absolute path: {}".format(e))
            # if Keyerror occurs, check for absolute path
            self.config = configparser.ConfigParser()
            self.config.read(config_file)
            self.comunioscore_schema = self.config.get('comunioscore', 'schema')

        self.comunioscore_table_auth = self.config.get('comunioscore', 'table_auth')
        self.comunioscore_table_communityuser = self.config.get('comunioscore', 'table_communityuser')
        self.comunioscore_table_squad = self.config.get('comunioscore', 'table_squad')
        self.comunioscore_table_season = self.config.get('comunioscore', 'table_season')

        # get database configs
        self.db_host     = self.config.get('database', 'host')
        self.db_port     = self.config.getint('database', 'port')
        self.db_user     = self.config.get('database', 'username')
        self.db_password = self.config.get('database', 'password')
        self.db_name     = self.config.get('database', 'dbname')

        # create database instances
        DBConnector.connect_psycopg(host=self.db_host, port=self.db_port, username=self.db_user,
                                    password=self.db_password, dbname=self.db_name, minConn=1, maxConn=5)
        self.dbcreator = DBCreator()
        self.dbinserter = DBInserter()
        self.dbfetcher = DBFetcher()

        # get telegram token
        self.telegram_token = self.config.get('telegram', 'token')

        # at start create all necessary tables for comunioscore
        self.__create_tables_for_communioscore()

    def __create_tables_for_communioscore(self):
        """ creates all necessary tables for application communioscore

        """
        # create schema if not exists comunioscore
        self.logger.info("create Schema {}".format(self.comunioscore_schema))
        self.dbcreator.build(obj=Schema(name=self.comunioscore_schema))

        # create table if not exists auth
        self.logger.info("create Table {}".format(self.comunioscore_table_auth))
        self.dbcreator.build(obj=Table(self.comunioscore_table_auth,
                                       Column(name="timestamp_utc", type="bigint"),
                                       Column(name="datetime", type="text"),
                                       Column(name="expires_in", type="Integer"),
                                       Column(name="expire_timestamp_utc", type="bigint"),
                                       Column(name="expire_datetime", type="text"),
                                       Column(name="access_token", type="text"),
                                       Column(name="token_type", type="text"),
                                       Column(name="refresh_token", type="text"),
                                       schema=self.comunioscore_schema))

        # create table if not exists communityuser
        self.logger.info("create Table {}".format(self.comunioscore_table_communityuser))
        self.dbcreator.build(obj=Table(self.comunioscore_table_communityuser,
                                     Column(name="userid", type="bigint", prim_key=True),
                                     Column(name="username", type="text"),
                                     Column(name="community", type="text"),
                                     Column(name="points", type="integer"),
                                     Column(name="teamvalue", type="bigint"),
                                     schema=self.comunioscore_schema))

        # create table if not exists squad
        self.logger.info("create Table {}".format(self.comunioscore_table_squad))
        self.dbcreator.build(obj=Table(self.comunioscore_table_squad,
                                     Column(name="userid", type="bigint"),
                                     Column(name="username", type="text"),
                                     Column(name="playername", type="text", prim_key=True),
                                     Column(name="playerposition", type="text"),
                                     Column(name="club", type="text"),
                                     schema=self.comunioscore_schema))

        self.logger.info("create Table {}".format(self.comunioscore_table_season))
        self.dbcreator.build(obj=Table(self.comunioscore_table_season,
                                       Column(name="match_day", type="Integer"),
                                       Column(name="match_type", type="text"),
                                       Column(name="match_id", type="bigint"),
                                       Column(name="start_timestamp", type="bigint"),
                                       Column(name="start_datetime", type="text"),
                                       Column(name="homeTeam", type="text"),
                                       Column(name="awayTeam", type="text"),
                                       Column(name="homeScore", type="text"),
                                       Column(name="awayScore", type="text"),
                                       schema=self.comunioscore_schema))



