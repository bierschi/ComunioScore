import logging


class LiveData:
    """ class LiveData to fetch live data from given match id

    USAGE:
            livedata = LiveData()
            livedata.fetch()

    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class LiveData')

    def fetch(self, match_day, match_id, home_team, away_team):

        print("Fetch data from match day {}: {} vs. {}".format(match_day, home_team, away_team))
