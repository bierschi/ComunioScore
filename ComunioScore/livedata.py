import logging
from ComunioScore.score import BundesligaScore
from ComunioScore import DBHandler
import random
from time import sleep
from threading import Thread

class LiveData(DBHandler):
    """ class LiveData to fetch live data from given match id

    USAGE:
            livedata = LiveData()
            livedata.fetch()

    """
    def __init__(self, season_date, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class LiveData')

        # init base class
        DBHandler.__init__(self, **dbparams)
        self.season_date = season_date

        # bundesligascore instance
        self.bundesliga = BundesligaScore(season_date=self.season_date)

        self.user_sql = "select userid, username from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_user)
        self.squad_sql = "select username, playername, club from {}.{} where userid = %s".format(self.comunioscore_schema, self.comunioscore_table_squad)

        self.comunio_users = self.dbfetcher.all(sql=self.user_sql)

    def get_comunio_data(self):
        """

        :return:
        """
        pass

    def fetch(self, match_day, match_id, home_team, away_team):
        """

        :param match_day:
        :param match_id:
        :param home_team:
        :param away_team:
        :return:
        """
        # TODO Thread
        live_data_msg = "Fetch live data from match day {}: {} vs. {}".format(match_day, home_team, away_team)
        self.logger.info(live_data_msg)
        if match_id == 8272232 or match_id == 8272213:
            for i in range(0, 5):
                self.logger.info("send data from match {} vs {}".format(home_team, away_team))
                sleep(random.randint(5, 10))
        # 1. get players from home team and away team of given match id
        # 2. check squad from each comunio user if a player in home or away team
        # 3. create new data structure for the relevant players
        # 4. request the current rating of the relevant players
        # 5. send telegram message periodically or with an command handler
        self.logger.info("Finished match {} vs {}".format(home_team, away_team))
