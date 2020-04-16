import logging
from ComunioScore.score import BundesligaScore


class LiveData:
    """ class LiveData to fetch live data from given match id

    USAGE:
            livedata = LiveData()
            livedata.fetch()

    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class LiveData')


    def get_comunio_data(self):
        """

        :return:
        """
        pass


    def fetch(self, match_day, match_id, home_team, away_team):

        print("Fetch data from match day {}: {} vs. {}".format(match_day, home_team, away_team))
        # 1. get players from home team and away team of given match id
        # 2. check squad from each comunio user if a player in home or away team
        # 3. create new data structure for the relevant players
        # 4. request the current rating of the relevant players
        # 5. send telegram message periodically or with an command handler
