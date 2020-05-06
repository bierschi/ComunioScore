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

        # check db params
        if (('host' and 'port' and 'username' and 'password' and 'dbname') in dbparams.keys()) and \
                (all(value is not None for value in dbparams.values())):
            self.db_host     = dbparams['host']
            self.db_port     = dbparams['port']
            self.db_username = dbparams['username']
            self.db_password = dbparams['password']
            self.db_name     = dbparams['dbname']

            # connect to postgres database
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
                self.postgres = True

                # at start create all necessary tables for comunioscore
                self.__create_tables_for_communioscore()

            else:
                self.logger.error("DBHandler could not connect to the postgres database")
                raise DBConnectorError("DBHandler could not connect to the postgres database")
        else:
            path = '/var/log/ComunioScore/comunioscore.db'

            if DBConnector.connect_sqlite(path=path):

                self.dbcreator = DBCreator()
                self.dbinserter = DBInserter()
                self.dbfetcher = DBFetcher()

                self.comunioscore_schema = "main"
                self.comunioscore_table_auth = "auth"
                self.comunioscore_table_user = "user"
                self.comunioscore_table_squad = "squad"
                self.comunioscore_table_season = "season"
                self.comunioscore_table_points = "points"
                self.postgres = False

                # at start create all necessary tables for comunioscore
                self.__create_tables_for_communioscore()
            else:
                self.logger.error("DBHandler could not connect to the sqlite database")
                raise DBConnectorError("DBHandler could not connect to the sqlite database")

    def __create_tables_for_communioscore(self):
        """ creates all necessary tables for application communioscore

        """

        # create schema if not exists comunioscore
        if self.postgres:
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

        # create table if not exists season
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

        # create table if not exists points
        self.logger.info("Create Table {}".format(self.comunioscore_table_points))
        self.dbcreator.build(obj=Table(self.comunioscore_table_points,
                                       Column(name="userid", type="bigint"),
                                       Column(name="username", type="text"),
                                       Column(name="match_id", type="bigint"),
                                       Column(name="match_day", type="Integer"),
                                       Column(name="homeTeam", type="text"),
                                       Column(name="awayTeam", type="text"),
                                       Column(name="points_rating", type="Integer"),
                                       Column(name="points_goal", type="Integer"),
                                       Column(name="points_off", type="Integer"),
                                       schema=self.comunioscore_schema))

    def update_points_in_database(self, userid, match_id, match_day, points_rating, points_goal, points_off):
        """ updates the points_rating, points_offs and points_goals per match in the database

        """
        points_sql = "update {}.{} set points_rating = %s, points_goal = %s, points_off = %s where userid = %s " \
                     "and match_day = %s and match_id = %s".format(self.comunioscore_schema, self.comunioscore_table_points)

        try:
            self.dbinserter.row(sql=points_sql, data=(points_rating, points_goal, points_off, userid, match_day, match_id))
        except DBInserterError as ex:
            self.logger.error(ex)

    def query_rating_goal_off_points(self, userid, match_day, match_id=None):
        """ queries points for rating, goal and offs from the points table in the database

        :return: list with data
        """

        if match_id is None:
            points_sql = "select points_rating, points_goal, points_off from {}.{} where userid = %s " \
                             "and match_day = %s".format(self.comunioscore_schema, self.comunioscore_table_points)
            points_sql_data = (userid, match_day)
        else:
            points_sql = "select points_rating, points_goal, points_off from {}.{} where userid = %s and match_day = %s " \
                         "and match_id = %s".format(self.comunioscore_schema, self.comunioscore_table_points)
            points_sql_data = (userid, match_day, match_id)

        try:
            data = self.dbfetcher.all(sql=points_sql, data=points_sql_data)
        except DBInserterError as ex:
            self.logger.error(ex)
            data = list()

        return data
