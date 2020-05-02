import unittest
from ComunioScore.score import BundesligaScore


class TestBundesligaScore(unittest.TestCase):

    def setUp(self) -> None:

        self.bundesliga = BundesligaScore(season_date="2019-08-20")
        self.match_id = None

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
        pass
        #lineup = self.bundesliga.lineup_from_match_id(match_id=self.match_id)
        #self.assertIsInstance(lineup, dict, msg="lineup must be type of dict")
        #self.assertIn('homeTeam', lineup, msg="lineup dict has no key homeTeam")
        #self.assertIn('awayTeam', lineup, msg="lineup dict has no key awayTeam")
        #self.assertIsInstance(lineup['homeTeam'], list, msg="lineup['homeTeam'] must be type of list")
        #self.assertIsInstance(lineup['awayTeam'], list, msg="lineup['awayTeam'] must be type of list")
        #for (homeplayer, awayplayer) in zip(lineup['homeTeam'], lineup['awayTeam']):
        #    self.assertIsInstance(homeplayer, dict, msg="homeplayer must be type of list")
        #    self.assertIsInstance(awayplayer, dict, msg="awayplayer must be type of list")

    def test_get_incidents_for_match(self):
        pass

    def test_season_data(self):

        season_data = self.bundesliga.season_data()
        self.assertIsInstance(season_data, list, msg="season data must be type of list")
        for matchday in season_data:
            if self.match_id is None:
                self.match_id = matchday['matchId']
                self.assertIsInstance(self.match_id, int, msg="match id must be type of int")
            self.assertIsInstance(matchday, dict, msg="matchday data must be type of dict")

    def test_is_finished(self):
        pass

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
