import os
import unittest
import configparser

from ComunioScore.score import SofaScore, BundesligaScore
from ComunioScore import ROOT_DIR


class TestBundesligaScore(unittest.TestCase):

    def setUp(self) -> None:

        # load local config file
        self.config = configparser.ConfigParser()
        self.config.read(ROOT_DIR + '/config/cfg.ini')

        # ScraperAPI config
        try:
            self.apikey = self.config.get('ScraperAPI', 'apikey')
        except (KeyError, configparser.NoSectionError) as e:
            self.apikey = os.environ['ScraperAPI']

        SofaScore.init_scraper(api_key=self.apikey)

        self.bundesliga = BundesligaScore()
        self.bundesliga.init_season_data(season_date="2020-05-15")

        self.match_id = "8272345"

    def test_ids_for_matchday(self):

        matchday_ids = self.bundesliga.ids_for_matchday(date="2019-10-05")
        self.assertIsInstance(matchday_ids, list, msg="matchday ids must be type of list")
        for match in matchday_ids:
            self.assertIsInstance(match, dict, msg="match must be type of dict")
            self.assertIn('id', match, msg="match dict has no key id")
            self.assertIn('match', match, msg="match dict has no key match")
            self.assertIn('homeTeam', match, msg="match dict has no key homeTeam")
            self.assertIn('awayTeam', match, msg="match dict has no key awayTeam")

    def test_lineup_from_match_id(self):

        lineup = self.bundesliga.lineup_from_match_id(match_id=self.match_id)

        self.assertIsInstance(lineup, dict, msg="lineup must be type of dict")
        self.assertIn('homeTeam', lineup, msg="lineup dict has no key homeTeam")
        self.assertIn('awayTeam', lineup, msg="lineup dict has no key awayTeam")
        self.assertIn('homeTeamIncidents', lineup, msg="lineup dict has no key homeTeamIncidents")
        self.assertIn('awayTeamIncidents', lineup, msg="lineup dict has no key awayTeamIncidents")
        self.assertIsInstance(lineup['homeTeam'], list, msg="lineup['homeTeam'] must be type of list")
        self.assertIsInstance(lineup['awayTeam'], list, msg="lineup['awayTeam'] must be type of list")
        self.assertIsInstance(lineup['homeTeamIncidents'], list, msg="lineup['homeTeamIncidents'] must be type of list")
        self.assertIsInstance(lineup['awayTeamIncidents'], list, msg="lineup['awayTeamIncidents'] must be type of list")
        for (homeplayer, awayplayer) in zip(lineup['homeTeam'], lineup['awayTeam']):
            self.assertIsInstance(homeplayer, dict, msg="homeplayer must be type of list")
            self.assertIsInstance(awayplayer, dict, msg="awayplayer must be type of list")

    def test_season_data(self):

        season_data = self.bundesliga.season_data()
        self.assertIsInstance(season_data, list, msg="season data must be type of list")
        for matchday in season_data:
            self.assertIsInstance(matchday, dict, msg="matchday data must be type of dict")

    def test_is_finished(self):

        is_finished = self.bundesliga.is_finished(matchid=self.match_id)
        self.assertTrue(is_finished, msg="is_finished must be True!")

    def tearDown(self) -> None:

        self.bundesliga.close()


if __name__ == '__main__':
    unittest.main()
