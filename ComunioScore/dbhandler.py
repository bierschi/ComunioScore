import logging

from ComunioScore.db import DBConnector, DBInserter, DBFetcher
from ComunioScore.db import DBCreator, Schema, Table, Column
from ComunioScore.exceptions import DBConnectorError, DBInserterError


class DBHandler:
    """ Base class DBHandler which provides database actions for subclasses

    USAGE:
            dbhandler = DBHandler()

    """
    def __init__(self, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class DBHandler')

        if ('host' and 'port' and 'username' and 'password' and 'dbname') in dbparams.keys():
            self.db_host     = dbparams['host']
            self.db_port     = dbparams['port']
            self.db_username = dbparams['username']
            self.db_password = dbparams['password']
            self.db_name     = dbparams['dbname']

            if DBConnector.connect_psycopg(host=self.db_host, port=self.db_port, username=self.db_username,
                                           password=self.db_password, dbname=self.db_name, minConn=1, maxConn=39):

                self.dbcreator = DBCreator()
                self.dbinserter = DBInserter()
                self.dbfetcher = DBFetcher()

                self.comunioscore_schema = "comunioscore"
                self.comunioscore_table_auth = "auth"
                self.comunioscore_table_user = "user"
                self.comunioscore_table_squad = "squad"
                self.comunioscore_table_season = "season"
                self.comunioscore_table_points = "points"

                # at start create all necessary tables for comunioscore
                self.__create_tables_for_communioscore()

            else:
                self.logger.error("DBHandler could not connect to the databases")
                raise DBConnectorError("DBHandler could not connect to the databases")
        else:
            self.logger.error("DBHandler could not connect to the databases")
            raise DBConnectorError("DBHandler could not connect to the databases")

    def __create_tables_for_communioscore(self):
        """ creates all necessary tables for application communioscore

        """

        # create schema if not exists comunioscore
        self.logger.info("Create Schema {}".format(self.comunioscore_schema))
        self.dbcreator.build(obj=Schema(name=self.comunioscore_schema))

        # create table if not exists auth
        self.logger.info("Create Table {}".format(self.comunioscore_table_auth))
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
        self.logger.info("Create Table {}".format(self.comunioscore_table_user))
        self.dbcreator.build(obj=Table(self.comunioscore_table_user,
                                     Column(name="userid", type="bigint", prim_key=True),
                                     Column(name="username", type="text"),
                                     Column(name="community", type="text"),
                                     Column(name="points", type="integer"),
                                     Column(name="teamvalue", type="bigint"),
                                     schema=self.comunioscore_schema))

        # create table if not exists squad
        self.logger.info("Create Table {}".format(self.comunioscore_table_squad))
        self.dbcreator.build(obj=Table(self.comunioscore_table_squad,
                                     Column(name="userid", type="bigint"),
                                     Column(name="username", type="text"),
                                     Column(name="playername", type="text", prim_key=True),
                                     Column(name="playerposition", type="text"),
                                     Column(name="club", type="text"),
                                     Column(name="linedup", type="text"),
                                     schema=self.comunioscore_schema))

        self.logger.info("Create Table {}".format(self.comunioscore_table_season))
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
                                       Column(name="season", type="text"),
                                       schema=self.comunioscore_schema))

        self.logger.info("Create Table {}".format(self.comunioscore_table_points))
        self.dbcreator.build(obj=Table(self.comunioscore_table_points,
                                       Column(name="userid", type="bigint"),
                                       Column(name="username", type="text"),
                                       Column(name="match_id", type="bigint"),
                                       Column(name="match_day", type="Integer"),
                                       Column(name="homeTeam", type="text"),
                                       Column(name="awayTeam", type="text"),
                                       Column(name="points", type="Integer"),
                                       schema=self.comunioscore_schema))

    def update_points_in_database(self, userid, match_id, match_day, points):
        """ updates the points per match in database

        """
        points_sql = "update {}.{} set points = %s where userid = %s and match_day = %s and match_id = %s".format(
                      self.comunioscore_schema, self.comunioscore_table_points)

        try:
            self.dbinserter.row(sql=points_sql, data=(points, userid, match_day, match_id))
        except DBInserterError as ex:
            self.logger.error(ex)


