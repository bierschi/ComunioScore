import logging
import datetime
from threading import Thread
from time import sleep, time

from ComunioScore import DBHandler
from ComunioScore import Comunio
from ComunioScore.exceptions import DBInserterError


class ComunioDB(DBHandler, Thread):
    """ class DBAgent to insert REST data into postgres database

    USAGE:
            dbagent = DBAgent(config_file='cfg.ini')
            dbagent.start()

    """
    def __init__(self, comunio_user, comunio_pass, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('create class DBAgent')

        # init base classes
        DBHandler.__init__(self, **dbparams)
        Thread.__init__(self)

        self.comunio_username = comunio_user
        self.comunio_password = comunio_pass

        # create comunio instance
        self.comunio = Comunio()


    def run(self) -> None:
        """

        :return:
        """
        pass

    def __comunio_login(self):
        """ tries to login into comunio

        :return: bool, True if login was successful
        """

        return self.comunio.login(username=self.comunio_username, password=self.comunio_password)

    def insert_comunio_user(self):
        """ insert comunio user into database

        """

        self.logger.info("insert comunio {} data into database".format(self.comunioscore_table_user))

        comuniouser = list()
        player_standings = self.comunio.get_player_standings()
        communityname = self.comunio.get_community_name()

        for player in player_standings:
            comuniouser.append((player['id'], player['name'], communityname, player['points'], player['teamValue']))

        sql = "insert into {}.{} (userid, username, community, points, teamvalue) values(%s, %s, %s, %s, %s)"\
              .format(self.comunioscore_schema, self.comunioscore_table_user)

        try:
            self.dbinserter.many_rows(sql=sql, datas=comuniouser)
        except DBInserterError as ex:
            self.logger.error(ex)

    def update_comunio_user(self):
        """ updates comunio user in the database

        """
        self.logger.info("updating comunio {} data in database".format(self.comunioscore_table_user))

        player_standings = self.comunio.get_player_standings()
        communityname = self.comunio.get_community_name()

        sql = "update {}.{} set username = %s, community = %s, points = %s, teamvalue = %s where userid = %s"\
              .format(self.comunioscore_schema, self.comunioscore_table_user)

        try:
            for player in player_standings:
                self.dbinserter.row(sql=sql, data=(player['name'], communityname, player['points'], player['teamValue'], player['id']))
        except DBInserterError as ex:
            self.logger.error(ex)
