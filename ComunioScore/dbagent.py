import threading
import logging
import configparser
from time import sleep
from ComunioScore.comunio import Comunio
from ComunioScore.db.connector import DBConnector
from ComunioScore.db.inserter import DBInserter
from ComunioScore.db.creator import DBCreator, Schema, Table, Column
from ComunioScore import ROOT_DIR


class DBAgent:
    """ class DBAgent for specific comunio database actions

    USAGE:
            dbagent = DBAgent()
            dbagent.start()
    """
    def __init__(self, config_file):
        self.logger = logging.getLogger('ComunioScoreApp')
        self.logger.info('create class DBAgent')

        self.config_file = config_file
        self.config = configparser.ConfigParser()

        # try first ini file in config folder
        self.config.read(ROOT_DIR + '/config/' + config_file)
        try:
            # check if keys are readable
            self.comunioscore_schema = self.config.get('comunioscore_database', 'schema')
        except (KeyError, configparser.NoSectionError) as e:
            self.logger.error("failed to load config file. Try to use absolute path: {}".format(e))
            # if Keyerror occurs, check for absolute path
            self.config = configparser.ConfigParser()
            self.config.read(config_file)
            self.comunioscore_schema = self.config.get('comunioscore_database', 'schema')

        self.comunioscore_table_communityuser = self.config.get('comunioscore_database', 'table_communityuser')
        self.comunioscore_table_squad = self.config.get('comunioscore_database', 'table_squad')

        # comunio config
        self.username = self.config.get('comunio', 'username')
        self.password = self.config.get('comunio', 'password')

        # database config
        self.db_host = self.config.get('database', 'host')
        self.db_port = self.config.getint('database', 'port')
        self.db_user = self.config.get('database', 'username')
        self.db_password = self.config.get('database', 'password')
        self.db_name = self.config.get('database', 'dbname')

        # create comunio class
        self.comunio = Comunio()
        self.comunio.login(username=self.username, password=self.password)

        # create database class
        DBConnector.connect(host=self.db_host, port=self.db_port, username=self.db_user, password=self.db_password,
                            dbname=self.db_name, minConn=1, maxConn=5)
        self.dbcreator = DBCreator()
        self.dbinserter = DBInserter()

        # create run thread
        self.__thread = threading.Thread(target=self.__run)
        self.__running = False

    def create_tables_for_communioscore(self):
        """ creates all necessary tables for application communioscore

        """
        # create schema if not exists comunioscore
        self.logger.info("create Schema {}".format(self.comunioscore_schema))
        self.dbcreator.build(obj=Schema(name=self.comunioscore_schema))

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

    def start(self, daemon=False):
        """ starts the run thread for dbagent

        """
        if self.__thread:
            if isinstance(daemon, bool):
                self.__thread.daemon = daemon
                self.__running = True
                self.logger.info("start the dbagent run thread")
                self.__thread.start()
            else:
                raise TypeError("'daemon' must be type of boolean")

    def stop(self):
        """ stops the run thread for dbagent

        """
        if self.__thread:
            self.__running = False
            self.logger.info("stop the dbagent run thread")
            self.__thread.join()

    def insert_communityuser(self):
        """ insert communityuser data into database

        """
        self.logger.info("insert communityuser data into dabase")
        communityuser = list()
        player_standings = self.comunio.get_player_standings()
        communityname = self.comunio.get_community_name()

        for player in player_standings:
            communityuser.append((player['id'], player['name'], communityname, player['points'], player['teamValue']))

        sql = "insert into {}.{} (userid, username, community, points, teamvalue) values(%s, %s, %s, %s, %s)".format(self.comunioscore_schema, self.comunioscore_table_communityuser)
        self.dbinserter.many_rows(sql=sql, datas=communityuser)

    def update_communityuser(self):
        """ updates communityuser data in database

        """
        self.logger.info("updating communityuser data")
        player_standings = self.comunio.get_player_standings()
        communityname = self.comunio.get_community_name()

        sql = "update {}.{} set username = %s, community = %s, points = %s, teamvalue = %s where userid = %s".format(self.comunioscore_schema, self.comunioscore_table_communityuser)

        for player in player_standings:
            self.dbinserter.row(sql=sql, data=(player['name'], communityname, player['points'], player['teamValue'], player['id']))

    def insert_squad(self):
        """ insert squad data into database

        """
        self.logger.info("insert squad data into database")
        users = self.comunio.get_comunio_user_data()
        sql = "insert into {}.{} (userid, username, playername, playerposition, club) values(%s, %s, %s, %s, %s)".format(self.comunioscore_schema, self.comunioscore_table_squad)
        for user in users:
            for player in user['squad']:
                self.dbinserter.row(sql=sql, data=(user['id'],user['name'], player['name'], player['position'], player['club']))

    def delete_communityuser(self):
        """ deletes communityuser data from database

        """
        self.logger.info("deleting communityuser data from database")
        sql = "delete from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_communityuser)
        self.dbinserter.sql(sql=sql)

    def delete_squad(self):
        """ deletes squad data from database

        """
        self.logger.info("deleting squad data from database")
        sql = "delete from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_squad)
        self.dbinserter.sql(sql=sql)

    def __run(self):
        """ run thread for dbagent

        """
        # at start create all necessary tables for comunioscore
        self.create_tables_for_communioscore()
        # delete all old entries from database tables
        self.delete_communityuser()
        self.delete_squad()
        # insert current data into database tables
        self.insert_communityuser()
        self.insert_squad()

        # go into endless loop
        while self.__running:
            print("loop")
            #sleep(43200)

            sleep(1)


if __name__ == '__main__':
    agent = DBAgent(config_file='cfg.ini')
    agent.start()
    #agent.delete_squad()


