import logging
from ComunioScore.score.sofascore import SofaScore


class BundesligaScore(SofaScore):
    """ class BundesligaScore to retrieve statistics from  Bundesliga matches

    USAGE:
            buli = BundesligaScore(date="2019-09-22)
            buli.get_matchday_lineup()
    """
    def __init__(self, date):
        self.logger = logging.getLogger('ComunioScoreApp')
        self.logger.info('create class BundesligaScore')

        # init base class
        super().__init__()

        self.date = date
        self.tournament_name = "Bundesliga"
        self.matchday_data_list = None

        self.date_data = self.get_date_data(date=self.date)
        self.matchday_data_list = self.get_id_for_match()

    def get_id_for_match(self):
        """ get ids for all matches on given date

        :return: list containing match ids, match names
        """

        matchday_data_list = list()
        tournaments = self.date_data['sportItem']['tournaments']
        for tournament in tournaments:
            if (tournament['tournament']['name'] == self.tournament_name) and (tournament['category']['name'] == 'Germany'):
                bundesliga_events = tournament['events']
                for event in bundesliga_events:
                    match = dict()
                    match['id'] = event['id']
                    match['match'] = event['name']
                    match['homeTeam'] = {'name': event['name'].split(' - ')[0]}
                    match['awayTeam'] = {'name': event['name'].split(' - ')[1]}
                    matchday_data_list.append(match)

        return matchday_data_list

    def get_matchday_lineup(self):
        """ get complete lineup for all matches

        :return: matchday data list (match, name, player, player rating)
        """
        if self.matchday_data_list is not None:
            for match in self.matchday_data_list:
                lineup = self.get_lineups_match(match_id=match['id'])
                players_home_team = lineup['homeTeam']['lineupsSorted']
                players_away_team = lineup['awayTeam']['lineupsSorted']
                home_lineup_list = list()
                away_lineup_list = list()
                for player in players_home_team:
                    home_player_dict =  dict()
                    home_player_dict['player_name'] = player['player']['name']
                    try:
                        home_player_dict['player_rating'] = player['rating']
                    except KeyError:
                        home_player_dict['player_rating'] = 'not_available'
                    home_lineup_list.append(home_player_dict)
                match['homeTeam'].update({'lineup': home_lineup_list})

                for player in players_away_team:
                    away_player_dict = dict()
                    away_player_dict['player_name'] = player['player']['name']
                    try:
                        away_player_dict['player_rating'] = player['rating']
                    except KeyError:
                        away_player_dict['player_rating'] = 'not_available'
                    away_lineup_list.append(away_player_dict)
                match['awayTeam'].update({'lineup': away_lineup_list})

            return self.matchday_data_list

    def vis_matches(self):
        """ visualizes players with player rating

        """

        matchday = self.get_matchday_lineup()
        for match in matchday:
            print("{} : {}".format(match['homeTeam']['name'], match['awayTeam']['name']))
            for (home_player, away_player) in zip(match['homeTeam']['lineup'], match['awayTeam']['lineup']):
                print("{}   {}   ------  {}   {}".format(home_player['player_name'], home_player['player_rating'],
                                                         away_player['player_name'], away_player['player_rating']))
            print("\n")


if __name__ == '__main__':
    b = BundesligaScore('2019-11-23')
    print(b.get_matchday_lineup())
    print(len(b.get_matchday_lineup()))