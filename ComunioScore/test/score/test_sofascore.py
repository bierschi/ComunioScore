import os
import unittest
import configparser

from ComunioScore.score import SofaScore
from ComunioScore import ROOT_DIR


@unittest.skip
class TestSofaScore(unittest.TestCase):

    def setUp(self) -> None:

        # load local config file
        self.config = configparser.ConfigParser()
        self.config.read(ROOT_DIR + '/config/cfg.ini')

        # ScraperAPI config
        try:
            self.apikey = self.config.get('ScraperAPI', 'apikey')
        except (KeyError, configparser.NoSectionError) as e:
            self.apikey = os.environ['ScraperAPI']

        self.sofascore = SofaScore()
        self.sofascore.init_scraper(api_key=self.apikey)
        self.season_id = 23538  # 19/20
        self.match_id = None
        self.get_season()

    def get_season(self):

        season_data = self.sofascore.get_season(season_id=self.season_id)
        self.assertIsInstance(season_data, dict, msg="season data must be type of dict")
        for tournament in season_data['tournaments']:
            for event in tournament['events']:
                self.match_id = event['id']
                self.assertIsInstance(self.match_id, int, msg="match id must be type of int")
                break

    def test_get_scraper_requests(self):

        scraper_requests = self.sofascore.get_scraper_requests()
        self.assertIsInstance(scraper_requests, dict, msg="ScraperAPI request info must be type of dict")

    def test_get_date_data(self):

        date_data = self.sofascore.get_date_data(date="2019-10-05")
        self.assertIsInstance(date_data, dict, msg="date data must be type of dict")

    def test_get_match_data(self):

        match_data = self.sofascore.get_match_data(match_id=self.match_id)
        self.assertIsInstance(match_data, dict, msg="match data must be type of dict")

    def test_get_lineups_match(self):

        lineup_data = self.sofascore.get_lineups_match(match_id=self.match_id)
        self.assertIsInstance(lineup_data, dict, msg="lineup data must be type of dict")

    def test_get_player_stats(self):

        player_stats = self.sofascore.get_player_stats(match_id=self.match_id, player_id=8959)
        self.assertIsInstance(player_stats, dict, msg="player stats must be type of dict")

    def tearDown(self) -> None:
        self.sofascore.close()


if __name__ == '__main__':
    unittest.main()
