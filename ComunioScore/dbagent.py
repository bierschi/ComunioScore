import configparser
from ComunioScore.comunio import Comunio
from ComunioScore.db.inserter import DBInserter
from ComunioScore import ROOT_DIR

config = configparser.ConfigParser()
config.read(ROOT_DIR + '/config/cfg.ini')


class DBAgent:

    def __init__(self):

        # comunio config
        self.username = config.get('comunio', 'username')
        self.password = config.get('comunio', 'password')

        # database config
        self.db_host = config.get('database', 'host')
        self.db_port = config.getint('database', 'port')
        self.db_user = config.get('database', 'username')
        self.db_password = config.get('database', 'password')
        self.db_name = config.get('database', 'dbname')

        # create comunio class
        self.comunio = Comunio()
        self.comunio.login(username=self.username, password=self.password)

        # create database class
        self.dbinserter = DBInserter()
        self.dbinserter.connect(host=self.db_host, port=self.db_port, username=self.db_user, password=self.db_password, dbname=self.db_name)

    def __create_tables_for_communioscore(self):
        """

        :return:
        """
        pass

    def load_and_insert_communityuser(self):
        """

        :return:
        """
        communityuser = list()
        player_standings = self.comunio.get_player_standings()
        communityname = self.comunio.get_community_name()

        for player in player_standings:
            communityuser.append((player['id'], player['name'], communityname, player['points'], player['teamValue']))

        sql = "insert into comunio.communityuser (id, username, community, points, teamvalue) values(%s, %s, %s, %s, %s)"
        self.dbinserter.many_rows(sql=sql, datas=communityuser)

    def load_and_insert_squad(self):
        """

        :return:
        """

        users = self.comunio.get_comunio_user_data()
        for user in users:
            print(user)


if __name__ == '__main__':
    agent = DBAgent()
    agent.load_and_insert_squad()