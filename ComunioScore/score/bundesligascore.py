import logging
from ComunioScore.score.sofascore import SofaScore


class BundesligaScore(SofaScore):
    """ class BundesligaScore to retrieve statistics from  Bundesliga matches

    USAGE:
            buli = BundesligaScore()
            buli.season_data()
    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('create class BundesligaScore')

        # init base class
        super().__init__()

        self.tournament_name = "Bundesliga"
        self.matchday_data_list = None
        self.season_id_19_20 = 23538  # TODO not hardcoded

    def ids_for_matchday(self, date):
        """ get ids for all matches on given date

        matchday_data_list = [
        {'id': 8272345, 'match': 'Hertha BSC - Fortuna Düsseldorf', 'homeTeam': {'name': 'Hertha BSC'}, 'awayTeam': {'name': 'Fortuna Düsseldorf'}},
        {'id': 8272011, 'match': 'Bayer 04 Leverkusen - RB Leipzig', 'homeTeam': {'name': 'Bayer 04 Leverkusen'}, 'awayTeam': {'name': 'RB Leipzig'}}
        ]

        :return: list containing match ids, match names, homeTeam, awayTeam
        """

        matchday_data_list = list()
        date_data = self.get_date_data(date=date)
        tournaments = date_data['sportItem']['tournaments']
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

    def lineup_from_match_id(self, match_id):
        """ get lineup for given match_id

        lineup = {'homeTeam': [{'player_name': 'Rune Jarstein', 'substitue': False, 'player_rating': '6.5'},
                               {'player_name': 'Lukas Klünter', 'substitue': False, 'player_rating': '6.5'}],
                  'awayTeam': [{'player_name': 'Zack Steffen', 'substitute': False, 'player_rating': '5.6'},
                               {'player_name': 'Matthias Zimmermann', 'substitute': False, 'player_rating': '6.3'}]}

        :return: lineup dict with 'homeTeam' and 'awayTeam'
        """

        lineup = self.get_lineups_match(match_id=match_id)
        players_home_team = lineup['homeTeam']['lineupsSorted']
        players_away_team = lineup['awayTeam']['lineupsSorted']
        lineup_dict = dict()
        home_lineup_list = list()
        away_lineup_list = list()
        for player in players_home_team:
            home_player_dict =  dict()
            home_player_dict['player_name'] = player['player']['name']
            home_player_dict['substitue']   = player['substitute']
            try:
                home_player_dict['player_rating'] = player['rating']
            except KeyError:
                home_player_dict['player_rating'] = 'not_available'
            home_lineup_list.append(home_player_dict)

        for player in players_away_team:
            away_player_dict = dict()
            away_player_dict['player_name'] = player['player']['name']
            away_player_dict['substitute']  = player['substitute']
            try:
                away_player_dict['player_rating'] = player['rating']
            except KeyError:
                away_player_dict['player_rating'] = 'not_available'
            away_lineup_list.append(away_player_dict)

        lineup_dict['homeTeam'] = home_lineup_list
        lineup_dict['awayTeam'] = away_lineup_list

        return lineup_dict

    def season_data(self):
        """ get season data from season id

        season_list =[
        {'matchDay': 1, 'type': 'finished', 'matchId': 8271917, 'startTimestamp': 1565980200, 'homeTeam': 'Bayern München', 'awayTeam': 'Hertha BSC', 'homeScore': 2, 'awayScore': 2},
        {'matchDay': 1, 'type': 'finished', 'matchId': 8271911, 'startTimestamp': 1566048600, 'homeTeam': 'Bayer 04 Leverkusen', 'awayTeam': 'SC Paderborn 07', 'homeScore': 3, 'awayScore': 2},
        {'matchDay': 1, 'type': 'finished', 'matchId': 8271912, 'startTimestamp': 1566048600, 'homeTeam': 'Freiburg', 'awayTeam': '1. FSV Mainz 05', 'homeScore': 3, 'awayScore': 0}
        ]

        :return: list with matchday infos as dicts
        """

        season_list = list()

        season_json = self.get_season(season_id=self.season_id_19_20)
        for tournament in season_json['tournaments']:
            for event in tournament['events']:
                season_dict = dict()
                season_dict['matchDay']       = event['roundInfo']['round']
                season_dict['type']           = event['status']['type']
                season_dict['matchId']        = event['id']
                season_dict['startTimestamp'] = event['startTimestamp']
                season_dict['homeTeam']       = event['homeTeam']['name']
                season_dict['awayTeam']       = event['awayTeam']['name']
                if event['status']['type'] == 'finished':
                    season_dict['homeScore'] = event['homeScore']['normaltime']
                    season_dict['awayScore'] = event['awayScore']['normaltime']
                else:
                    season_dict['homeScore'] = '-'
                    season_dict['awayScore'] = '-'
                season_list.append(season_dict)

        return season_list

    def is_finished(self, matchid):
        """ checks if a match has finished

        :return: bool, true or false
        """
        events = self.get_match_data(match_id=matchid)
        if 'event' in events:
            status = events['event']['status']['type']
            if status == 'finished':
                return True
            else:
                return False
        else:
            self.logger.error("no 'event' in self.get_match_data")

    def vis_lineup_with_rating(self, matchid):
        """ visualizes players with player rating

        """

        lineup = self.lineup_from_match_id(match_id=matchid)
        #print(lineup)
        for (homeplayer, awayplayer) in zip(lineup['homeTeam'], lineup['awayTeam']):
            print("{}({}) :  {}({})".format(homeplayer['player_name'], homeplayer['player_rating'],
                                                     awayplayer['player_name'], awayplayer['player_rating']))


if __name__ == '__main__':
    b = BundesligaScore()
    print(b.lineup_from_match_id(match_id=8272022))
    #b.vis_lineup_with_rating(8272006)
    #print(b.is_finished(8272006))