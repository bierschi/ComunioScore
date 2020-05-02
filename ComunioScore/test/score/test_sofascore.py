import unittest
from ComunioScore.score import SofaScore


class TestSofaScore(unittest.TestCase):

    def setUp(self) -> None:

        self.sofascore = SofaScore()
        self.season_id = 23538  # 19/20
        self.match_id = None
        self.get_season()

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

    def get_season(self):

        season_data = self.sofascore.get_season(season_id=self.season_id)
        self.assertIsInstance(season_data, dict, msg="season data must be type of dict")
        for tournament in season_data['tournaments']:
            for event in tournament['events']:
                self.match_id = event['id']
                self.assertIsInstance(self.match_id, int, msg="match id must be type of int")
                break

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
