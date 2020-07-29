import logging
import datetime
from threading import Thread
from time import sleep, time

from ComunioScore import DBHandler
from ComunioScore import Comunio
from ComunioScore.exceptions import DBInserterError


class ComunioDB(DBHandler, Thread):
    """ class ComunioDB to insert comunio data into database tables

    USAGE:
            comuniodb = ComunioDB(comunio_user='', comunio_pass='', update_frequence=21600, **dbparams)
            comuniodb.start()

    """
    def __init__(self, comunio_user, comunio_pass, update_frequence=7200, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class ComunioDB')

        # init base classes
        DBHandler.__init__(self, **dbparams)
        Thread.__init__(self)

        self.comunio_username = comunio_user
        self.comunio_password = comunio_pass
        self.update_frequence = update_frequence

        # create comunio instance
        self.comunio = Comunio()

        self.running = True

        self.user_data = None

    def run(self) -> None:
        """ run thread for class ComunioDB

        """

        self.comunio.login(username=self.comunio_username, password=self.comunio_password)

        # at start delete data from database tables
        self.delete_comunio_user()
        self.delete_squad()

        sleep(1)

        # insert comunio data first time into database tables
        self.insert_comunio_user()
        self.insert_squad()

        self.logger.info("Start Comuniodb run thread!")
        while self.running:
            sleep(self.update_frequence)  # updates comunio data every 6h (21600)

            # ensure the access token is valid
            self.comunio.login(username=self.comunio_username, password=self.comunio_password)
            self.delete_squad()
            self.update_comunio_user()
            self.update_squad()

    def insert_comunio_user(self):
        """ insert comunio user into database

        """

        self.logger.info("Comuniodb insert comunio {} data into database".format(self.comunioscore_table_user))

        comuniouser = list()

        self.user_data = self.comunio.get_all_user_points_and_teamvalues()
        communityname = self.comunio.get_community_name()

        for user in self.user_data:
            comuniouser.append((user['id'], user['login'], user['name'], communityname, user['points'], user['teamValue']))

        sql = "insert into {}.{} (userid, login, username, community, points, teamvalue) values(%s, %s, %s, %s, %s, %s)"\
              .format(self.comunioscore_schema, self.comunioscore_table_user)

        try:
            self.dbinserter.many_rows(sql=sql, datas=comuniouser)
        except DBInserterError as ex:
            self.logger.error(ex)

    def update_comunio_user(self):
        """ updates comunio user data in the database table

        """
        self.logger.info("Comuniodb updating comunio {} data in database".format(self.comunioscore_table_user))

        self.user_data = self.comunio.get_all_user_points_and_teamvalues()
        communityname = self.comunio.get_community_name()

        sql = "update {}.{} set login = %s, username = %s, community = %s, points = %s, teamvalue = %s where userid = %s"\
              .format(self.comunioscore_schema, self.comunioscore_table_user)

        try:
            for user in self.user_data:
                self.dbinserter.row(sql=sql, data=(user['login'], user['name'], communityname, user['points'],
                                                   user['teamValue'], user['id']))
        except DBInserterError as ex:
            self.logger.error(ex)

    def delete_comunio_user(self):
        """ deletes comunio user data from database

        """
        self.logger.info("Comuniodb deleting comunio {} data from database".format(self.comunioscore_table_user))

        sql = "delete from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_user)

        try:
            self.dbinserter.sql(sql=sql)
        except DBInserterError as ex:
            self.logger.error(ex)

    def insert_squad(self):
        """ inserts squad data into database

        """
        self.logger.info("Comuniodb insert {} data into database".format(self.comunioscore_table_squad))

        users_squads = self.comunio.get_all_user_squads()
        sql = "insert into {}.{} (userid, username, playername, playerposition, club, linedup) values(%s, %s, %s, %s, %s, %s)"\
              .format(self.comunioscore_schema, self.comunioscore_table_squad)

        try:
            for user in users_squads:
                for player in user['squad']:
                    self.dbinserter.row(sql=sql, data=(user['id'], user['name'], player['name'], player['position'],
                                                       player['club'], player['linedup']), autocommit=True)
        except DBInserterError as ex:
            self.logger.error(ex)

    def update_squad(self):
        """ updates the squad data from comunio user

        """
        self.logger.info("Comuniodb updating {} data".format(self.comunioscore_table_squad))

        users_squads = self.comunio.get_all_user_squads()
        sql = "insert into {}.{} (userid, username, playername, playerposition, club, linedup) values(%s, %s, %s, %s, %s, %s)"\
              .format(self.comunioscore_schema, self.comunioscore_table_squad)
        try:
            for user in users_squads:
                self.dbinserter.sql(sql="delete from {}.{} where userid = {}".format(self.comunioscore_schema, self.comunioscore_table_squad, int(user['id'])))

                for player in user['squad']:
                    self.dbinserter.row(sql=sql, data=(user['id'], user['name'], player['name'], player['position'], player['club'], player['linedup']))
        except DBInserterError as ex:
            self.logger.error(ex)

    def delete_squad(self):
        """ deletes squad data from database

        """

        self.logger.info("Comuniodb deleting {} data from database".format(self.comunioscore_table_squad))

        if self.postgres:
            sql = "truncate {}.{}".format(self.comunioscore_schema, self.comunioscore_table_squad)
        else:
            sql = "delete from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_squad)

        try:
            self.dbinserter.sql(sql=sql, autocommit=True)
        except DBInserterError as ex:
            self.logger.error(ex)

    def get_comunio_user_data(self):
        """ get comunio user data

        :return: dict with comunio user data
        [{'id': '252213', 'login': 'test', 'name': 'test', 'points': 0, 'teamValue': 52660000}, {'id': '2233653', 'login': 'test2', 'name': 'test2', 'points': 0, 'teamValue': 73310000}]
        """
        return self.user_data

    def update_linedup_squad(self):
        """ updates linedup squad in database table

        """
        self.logger.info("Comuniodb updating linedup squad in database table {}.{}".format(self.comunioscore_schema, self.comunioscore_table_squad))

        user_sql = "select userid from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_user)
        linedup_sql = "update {}.{} set linedup = %s where userid = %s and playername = %s".format(self.comunioscore_schema, self.comunioscore_table_squad)

        # ensure the access token is valid
        self.comunio.login(username=self.comunio_username, password=self.comunio_password)

        comunio_users = self.dbfetcher.all(sql=user_sql)
        for user in comunio_users:
            userid = user[0]
            squad = self.comunio.get_squad(userid=userid)
            for player in squad:
                playername = player['name']
                linedup    = player['linedup']
                try:
                    self.dbinserter.row(sql=linedup_sql, data=(linedup, userid, playername))
                except DBInserterError as ex:
                    self.logger.error(ex)

    def insert_auth(self):
        """ insert comunio auth data into database

        """
        self.logger.info("Insert auth data into database")

        ts_utc = int(str(time()).split('.')[0])
        dt = str(datetime.datetime.now())
        auth = self.comunio.get_auth_info()
        exp_ts_utc = int(str(time()).split('.')[0]) + int(auth['expires_in'])
        exp_dt = datetime.datetime.fromtimestamp(exp_ts_utc)

        sql = "insert into {}.{} (timestamp_utc, datetime, expires_in, expire_timestamp_utc, expire_datetime, " \
              "access_token, token_type, refresh_token) values (%s, %s, %s, %s, %s, %s, %s, %s)".format(self.comunioscore_schema, self.comunioscore_table_auth)

        try:
            self.dbinserter.row(sql=sql, data=(ts_utc, dt, auth['expires_in'], exp_ts_utc, exp_dt, auth['access_token'],
                                               auth['token_type'], auth['refresh_token']))
        except DBInserterError as ex:
            self.logger.error(ex)

    def delete_auth(self):
        """ deletes the auth entries from database

        """
        self.logger.info("Deleting auth data from database")

        sql = "delete from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_auth)

        try:
            self.dbinserter.sql(sql=sql)
        except DBInserterError as ex:
            self.logger.error(ex)


