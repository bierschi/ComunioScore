import logging
from time import sleep

from ComunioScore.score.sofascore import SofaScore
from ComunioScore.exceptions import SofascoreRequestError


class BundesligaScore(SofaScore):
    """ class BundesligaScore to retrieve statistics from Bundesliga matches

    USAGE:
            buli = BundesligaScore()
            buli.season_data()
    """
    season_name = None  # Bundesliga 19/20
    season_year = None  # 19/20
    season_id   = None  # 23583

    def __init__(self, season_date):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class BundesligaScore')

        # init base class
        super().__init__()

        self.season_date = season_date

        self.__check_season_data()

        self.matchday_data_list = None

    def __check_season_data(self):
        """ checks if season data are set

        """
        if BundesligaScore.season_name is None:
            self.__set_current_season()
        else:
            self.logger.info("Season data already set!")

    def __set_current_season(self):
        """ sets the current season data

        """

        date = self.season_date.split('-')
        if len(date) > 2:
            date_day = int(date[2])
            date_month = date[1]
            date_year = date[0]

            for i in range(0, 7):
                if (date_day + i) < 10:
                    query_date_day = date_day + i
                    query_date_day = "0" + str(query_date_day)
                else:
                    query_date_day = str(date_day + i)

                if self.__get_current_season_data(date="{}-{}-{}".format(date_year, date_month, query_date_day)):
                    self.logger.info("Set current season data to {}".format(self.season_name))
                    break
                else:
                    sleep(1)
        else:
            self.logger.error("Could not parse season date: {}".format(self.season_date))

    def __get_current_season_data(self, date):
        """ requests the current season data from sofascore with given date

        :return: True if Bundesliga season was found, else False
        """

        try:
            season_data = self.get_date_data(date=date)
        except SofascoreRequestError as ex:
            self.logger.error(ex)
            return False

        if 'sportItem' in season_data:
            for tournaments in season_data['sportItem']['tournaments']:

                # Find tournament bundesliga
                if tournaments['tournament']['name'] == 'Bundesliga':
                    # German bundesliga only
                    if tournaments['category']['name'] == 'Germany':
                        BundesligaScore.season_name = tournaments['season']['name']
                        BundesligaScore.season_year = tournaments['season']['year']
                        BundesligaScore.season_id   = tournaments['season']['id']
                        return True
                    else:
                        pass
                        #self.logger.error("No category 'Germany' in Bundesliga")

                else:
                    pass
                    #self.logger.error("No tournament 'Bundesliga' was found")
        else:
            pass

        return False

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
            if (tournament['tournament']['name'] == 'Bundesliga') and (tournament['category']['name'] == 'Germany'):
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

        relevant_incidents = self._get_incidents_for_match(lineup=lineup)

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
                home_player_dict['player_rating'] = '–'
            home_lineup_list.append(home_player_dict)

        for player in players_away_team:
            away_player_dict = dict()
            away_player_dict['player_name'] = player['player']['name']
            away_player_dict['substitute']  = player['substitute']
            try:
                away_player_dict['player_rating'] = player['rating']
            except KeyError:
                away_player_dict['player_rating'] = '–'
            away_lineup_list.append(away_player_dict)

        lineup_dict['homeTeam'] = home_lineup_list
        lineup_dict['awayTeam'] = away_lineup_list
        lineup_dict['homeTeamIncidents'] = relevant_incidents['home_team_incidents']
        lineup_dict['awayTeamIncidents'] = relevant_incidents['away_team_incidents']

        return lineup_dict

    def _get_incidents_for_match(self, lineup):
        """ get all incidents for a specific match

        :param lineup: lineup stats for given match

        :return: relevant_incidents
        """

        relevant_incidents = dict()

        home_team_incidents_list = list()
        if 'incidents' in lineup['homeTeam']:
            home_team_incidents = lineup['homeTeam']['incidents']
            for incident in home_team_incidents:
                for inc in home_team_incidents[incident]:
                    if 'incidentType' in inc:
                        # goal incident
                        if inc['incidentType'] == 'goal':
                            incidents_hometeam = dict()
                            incidents_hometeam['type'] = 'goal'
                            incidents_hometeam['class'] = inc['incidentClass']
                            incidents_hometeam['player'] = inc['player']['name']
                            home_team_incidents_list.append(incidents_hometeam)
                        # yellowRed, Red incident
                        if (inc['incidentType'] == 'card') and ((inc['type'] == 'YellowRed') or (inc['type'] == 'Red')):
                            incidents_hometeam = dict()
                            incidents_hometeam['type'] = 'card'
                            incidents_hometeam['class'] = inc['type']
                            incidents_hometeam['player'] = inc['player']['name']
                            home_team_incidents_list.append(incidents_hometeam)

        away_team_incidents_list = list()
        if 'incidents' in lineup['awayTeam']:
            away_team_incidents = lineup['awayTeam']['incidents']
            for incident in away_team_incidents:
                for inc in away_team_incidents[incident]:
                    if 'incidentType' in inc:
                        # goal incident
                        if inc['incidentType'] == 'goal':
                            incidents_awayteam = dict()
                            incidents_awayteam['type'] = 'goal'
                            incidents_awayteam['class'] = inc['incidentClass']
                            incidents_awayteam['player'] = inc['player']['name']
                            away_team_incidents_list.append(incidents_awayteam)
                        # yellowRed, Red incident
                        if (inc['incidentType'] == 'card') and ((inc['type'] == 'YellowRed') or (inc['type'] == 'Red')):
                            incidents_awayteam = dict()
                            incidents_awayteam['type'] = 'card'
                            incidents_awayteam['class'] = inc['type']
                            incidents_awayteam['player'] = inc['player']['name']
                            away_team_incidents_list.append(incidents_awayteam)

        relevant_incidents['home_team_incidents'] = home_team_incidents_list
        relevant_incidents['away_team_incidents'] = away_team_incidents_list

        return relevant_incidents

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
        try:
            if BundesligaScore.season_id:
                season_json = self.get_season(season_id=BundesligaScore.season_id)
            else:
                self.logger.error("Season id is not set. Could not load season data!")
                return season_list
        except SofascoreRequestError as ex:
            self.logger.error(ex)
            return season_list

        if 'tournaments' in season_json:
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
        else:
            self.logger.error("KeyError: 'tournaments' not in season_data")
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
            return True


if __name__ == '__main__':
    b = BundesligaScore(season_date="2019-08-18")
    print(b.lineup_from_match_id(match_id=8272182))
    #print(b.is_finished(8272006))
