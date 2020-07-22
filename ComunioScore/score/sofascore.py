import logging
import requests

from scraper_api import ScraperAPIClient


class SofaScore:
    """ Base class SofaScore to retrieve statistics from  sofascore.com

    USAGE:
            sofascore = SofaScore()
            sofascore.get_date_data(date="2019-09-22")

    """
    scraper = None

    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class SofaScore')

        self.session = requests.Session()

        # urls to retrieve specific data
        self.date_url         = "https://www.sofascore.com/football//{date}/json"  # yyyy-mm-dd
        self.event_url        = "https://www.sofascore.com/event/{event_id}/json"
        self.lineups_url      = "https://www.sofascore.com/event/{event_id}/lineups/json"
        self.player_stats_url = "https://www.sofascore.com/event/{event_id}/player/{player_id}/statistics/json"
        self.season_url       = "http://api.sofascore.com/mobile/v4/unique-tournament/35/season/{season_id}/events"

        self.headers = {'Accept': 'application/json'}

    @classmethod
    def init_scraper(cls, api_key):
        """ inits the scraper client

        """

        # create the ScraperAPIClient
        cls.scraper = ScraperAPIClient(api_key)

    def __request_api(self, url):
        """ request data from sofascore url

        :param url: specific url depending on requested data

        :return: json dict
        """
        try:
            return SofaScore.scraper.get(url=url).json()
        except requests.exceptions.RequestException as ex:
            self.logger.error("Could no retrieve data from Sofascore: {}".format(ex))
            return {}
        except ValueError as ex:
            self.logger.error(ex)
            return {}

    def get_date_data(self, date):
        """ get data from given date

        :param date: date string: "2019-09-22"
        :return: json dict
        """

        # create correct url
        date_url = self.date_url.format(date=date)

        return self.__request_api(url=date_url)

    def get_match_data(self, match_id):
        """ get data from given match id

        :param match_id: number for a specific match
        :return: json dict
        """

        # create correct url
        match_url = self.event_url.format(event_id=match_id)

        return self.__request_api(url=match_url)

    def get_lineups_match(self, match_id):
        """ get squad lineups for given match id

        :param match_id: number for a specific match
        :return: json dict
        """
        # create correct url
        lineups_url = self.lineups_url.format(event_id=match_id)

        return self.__request_api(url=lineups_url)

    def get_player_stats(self, match_id, player_id):
        """ get stats from given player and match

        :param match_id: id from match
        :param player_id: id from player
        :return: json dict
        """
        # create correct url
        player_stats_url = self.player_stats_url.format(event_id=match_id, player_id=player_id)

        return self.__request_api(url=player_stats_url)

    def get_season(self, season_id):
        """ get season data from given season_id

        :param season_id: unique id for sofascore
        :return: json dict
        """
        season_url = self.season_url.format(season_id=season_id)

        return self.__request_api(url=season_url)


