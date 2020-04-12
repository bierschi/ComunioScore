import logging
import threading
import datetime
from time import sleep, time

from ComunioScore import DBHandler
from ComunioScore import Comunio
from ComunioScore.score import BundesligaScore


class DBAgent(DBHandler):
    """ class DBAgent to insert REST data into postgres database

    USAGE:
            dbagent = DBAgent(config_file='cfg.ini')
            dbagent.start()

    """
    def __init__(self, comunio_user, comunio_pass, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('create class DBAgent')

        # init base class
        super().__init__(**dbparams)

        self.username = comunio_user
        self.password = comunio_pass

        # create comunio instance
        self.comunio = Comunio()

        # create BundesligaScore instance
        self.bundesliga = BundesligaScore()

        # create run thread
        self.__thread = threading.Thread(target=self.__run)
        self.__running = False

    def __del__(self):
        pass

    def start(self, daemon=False):
        """ starts the run thread for restdb

        """

        if self.__thread:
            if isinstance(daemon, bool):
                self.__thread.daemon = daemon
                self.__running = True
                self.logger.info("start the restdb run thread")
                self.__thread.start()
            else:
                raise TypeError("'daemon' must be type of boolean")

    def stop(self):
        """ stops the run thread for restdb

        """
        if self.__thread:
            self.__running = False
            self.logger.info("stop the restdb run thread")
            self.__thread.join()

    def __comunio_login(self):
        """ tries to login into comunio

        :return: bool, True if login was successful
        """

        return self.comunio.login(username=self.username, password=self.password)

    def __insert_auth(self):
        """ insert comunio auth data into database

        """
        self.logger.info("insert auth data into database")
        ts_utc = int(str(time()).split('.')[0])
        dt = str(datetime.datetime.now())
        auth = self.comunio.get_auth_info()
        exp_ts_utc = int(str(time()).split('.')[0]) + int(auth['expires_in'])
        exp_dt = datetime.datetime.fromtimestamp(exp_ts_utc)

        sql = "insert into {}.auth (timestamp_utc, datetime, expires_in, expire_timestamp_utc, expire_datetime, access_token, token_type, refresh_token) values (%s, %s, %s, %s, %s, %s, %s, %s)".format(self.comunioscore_schema)
        self.dbinserter.row(sql=sql, data=(ts_utc, dt, auth['expires_in'], exp_ts_utc, exp_dt, auth['access_token'], auth['token_type'], auth['refresh_token']))

    def __delete_auth(self):
        """ deletes the auth entries from database

        """
        self.logger.info("deleting auth data from database")
        sql = "delete from {}.auth".format(self.comunioscore_schema)
        self.dbinserter.sql(sql=sql)

    def __insert_communityuser(self):
        """ insert communityuser data into database

        """
        self.logger.info("insert {} data into dabase".format(self.comunioscore_table_communityuser))
        communityuser = list()
        player_standings = self.comunio.get_player_standings()
        communityname = self.comunio.get_community_name()

        for player in player_standings:
            communityuser.append((player['id'], player['name'], communityname, player['points'], player['teamValue']))

        sql = "insert into {}.{} (userid, username, community, points, teamvalue) values(%s, %s, %s, %s, %s)".format(self.comunioscore_schema, self.comunioscore_table_communityuser)
        self.dbinserter.many_rows(sql=sql, datas=communityuser)

    def __update_communityuser(self):
        """ updates communityuser data in database

        """
        self.logger.info("updating {} data".format(self.comunioscore_table_communityuser))
        player_standings = self.comunio.get_player_standings()
        communityname = self.comunio.get_community_name()

        sql = "update {}.{} set username = %s, community = %s, points = %s, teamvalue = %s where userid = %s".format(self.comunioscore_schema, self.comunioscore_table_communityuser)

        for player in player_standings:
            self.dbinserter.row(sql=sql, data=(player['name'], communityname, player['points'], player['teamValue'], player['id']))

    def __delete_communityuser(self):
        """ deletes communityuser data from database

        """
        self.logger.info("deleting {} data from database".format(self.comunioscore_table_communityuser))
        sql = "delete from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_communityuser)
        self.dbinserter.sql(sql=sql)

    def __insert_squad(self):
        """ insert squad data into database

        """
        self.logger.info("insert {} data into database".format(self.comunioscore_table_squad))
        users = self.comunio.get_comunio_user_data()
        sql = "insert into {}.{} (userid, username, playername, playerposition, club) values(%s, %s, %s, %s, %s)".format(self.comunioscore_schema, self.comunioscore_table_squad)

        for user in users:
            for player in user['squad']:
                self.dbinserter.row(sql=sql, data=(user['id'],user['name'], player['name'], player['position'], player['club']), autocommit=True)

    def __update_squad(self):
        """ updates the squad data from comunio members

        """
        self.logger.info("updating {} data".format(self.comunioscore_table_squad))
        users = self.comunio.get_comunio_user_data()
        sql = "insert into {}.{} (userid, username, playername, playerposition, club) values(%s, %s, %s, %s, %s)".format(
            self.comunioscore_schema, self.comunioscore_table_squad)

        for user in users:
            self.dbinserter.sql(sql="delete from comunioscore.squad where userid = {}".format(int(user['id'])))
            for player in user['squad']:
                self.dbinserter.row(sql=sql, data=(user['id'],user['name'], player['name'], player['position'], player['club']))

    def __delete_squad(self):
        """ deletes squad data from database

        """

        self.logger.info("deleting {} data from database".format(self.comunioscore_table_squad))
        sql = "truncate {}.{}".format(self.comunioscore_schema, self.comunioscore_table_squad)
        self.dbinserter.sql(sql=sql, autocommit=True)

    def __insert_season(self):
        """ insert season data into database

        """
        self.logger.info("insert season data into database")
        sql = "insert into {}.season (match_day, match_type, match_id, start_timestamp, start_datetime, homeTeam, awayTeam, homeScore, awayScore) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.comunioscore_schema)
        season_data = self.bundesliga.season_data()
        season_list = list()

        for matchday in season_data:
            start_dt = datetime.datetime.fromtimestamp(matchday['startTimestamp'])
            season_list.append((matchday['matchDay'], matchday['type'], matchday['matchId'], matchday['startTimestamp'], start_dt,matchday['homeTeam'], matchday['awayTeam'], matchday['homeScore'], matchday['awayScore']))

        self.dbinserter.many_rows(sql=sql, datas=season_list)

    def __update_season(self):
        """ updates season data into database

        """
        self.logger.info("updating season data")
        season_data = self.bundesliga.season_data()
        sql = "update {}.season set match_type = %s, homeScore = %s, awayScore = %s where match_id = %s".format(self.comunioscore_schema)
        for matchday in season_data:
            self.dbinserter.row(sql=sql, data=(matchday['type'], matchday['homeScore'], matchday['awayScore'], matchday['matchId']))

    def __delete_season(self):
        """ deletes season data from database

        """
        self.logger.info("deleting season data from database")
        sql = "delete from {}.season".format(self.comunioscore_schema)
        self.dbinserter.sql(sql=sql, autocommit=True)

    def __run(self):
        """ run thread for restdb

        """
        while not self.comunio.login(username=self.username, password=self.password):
            self.logger.error("could not login into comunio")
            sleep(60)

        # delete all old entries from database tables
        self.__delete_communityuser()
        self.__delete_squad()
        self.__delete_auth()
        self.__delete_season()

        # insert comunio data into database tables
        self.__insert_communityuser()
        self.__insert_squad()
        self.__insert_auth()
        # insert season data into database
        self.__insert_season()

        # go into endless loop
        while self.__running:

            if self.__comunio_login():
                self.__insert_auth()
                self.__update_communityuser()
                self.__update_squad()

            else:
                self.logger.error("could not login into comunio")
                sleep(60)

            self.__update_season()
            sleep(21600)  # updates data every 6 hour


if __name__ == '__main__':
    agent = DBAgent(config_file='cfg.ini')
    agent.start()
