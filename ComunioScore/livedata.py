import logging
from difflib import SequenceMatcher

from ComunioScore import DBHandler
from ComunioScore.messenger import ComunioScoreTelegram
from ComunioScore.score import BundesligaScore

import random
from time import sleep


class LiveData(DBHandler):
    """ class LiveData to fetch live data from given match id

    USAGE:
            livedata = LiveData()
            livedata.fetch()

    """
    def __init__(self, season_date, token, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class LiveData')

        # init base class
        DBHandler.__init__(self, **dbparams)
        # set attributes
        self.season_date = season_date
        self.token = token

        # bundesligascore instance
        self.bundesliga = BundesligaScore(season_date=self.season_date)

        # create telegram instance
        self.telegram = ComunioScoreTelegram(token=self.token)

        self.user_sql = "select userid, username from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_user)
        self.squad_sql = "select playername, club from {}.{} where userid = %s".format(self.comunioscore_schema, self.comunioscore_table_squad)

        self.comunio_users = self.dbfetcher.all(sql=self.user_sql)

    def fetch(self, match_day, match_id, home_team, away_team):
        """ fetches live data from given match id for comunio players of interest

        :param match_day: current match day
        :param match_id: match id for sofascore
        :param home_team: home team
        :param away_team: away team

        """

        live_data_start_msg = "Start fetching live data from match day {}: *{}* vs. *{}*".format(match_day, home_team, away_team)
        self.logger.info(live_data_start_msg)
        self.telegram.new_msg(live_data_start_msg)

        # get all comunio players of interest for sofascore rating
        players_of_interest_for_match = self.set_comunio_players_of_interest_for_match(home_team=home_team, away_team=away_team)

        # get match lineup from match id
        match_lineup = self.bundesliga.lineup_from_match_id(match_id=match_id)

        self.map_players_of_interest_with_match_lineup(players_of_interest=players_of_interest_for_match, match_lineup=match_lineup)
        # while not finished
        #if match_id == 8272232 or match_id == 8272213:
        #    for i in range(0, 5):
        #        self.logger.info("send data from match {} vs {}".format(home_team, away_team))
        #        sleep(random.randint(5, 10))

        # 1. get players from home team and away team of given match id
        # 2. check squad from each comunio user if a player in home or away team
        # 3. create new data structure for the relevant players
        # 4. request the current rating of the relevant players
        # 5. send telegram message periodically or with an command handler

        live_data_end_msg = "Finished fetching live data from match *{}* vs *{}*".format(home_team, away_team)
        self.logger.info(live_data_end_msg)

    def set_comunio_players_of_interest_for_match(self, home_team, away_team):
        """ sets all comunio players of interest for current match

        :return: list with all comunio players of interest
        [{'user': 'Shaggy', 'squad': [('Jorge Meré', '1. FC Köln'), ('Bornauw', '1. FC Köln')]}, ...]
        """
        # complete player list of interest for rest query to sofascore
        all_players_of_interest_for_rating_query = list()

        # iterate over all comunio users
        for user in self.comunio_users:
            user_id = user[0]
            user_name = user[1]

            # get current squad (player,club) with userid from database
            squad = self.dbfetcher.all(sql=self.squad_sql, data=(user_id,))

            # player list of interest for one comunio user
            player_list_per_user = list()

            # check if comunio player in home or away team
            for player in squad:
                team = player[1]
                if (team == home_team) or (team == away_team):
                    player_list_per_user.append(player)
                else:
                    hometeam_ratio = SequenceMatcher(None, team, home_team).ratio()
                    awayteam_ratio = SequenceMatcher(None, team, away_team).ratio()
                    if (hometeam_ratio > 0.6) or (awayteam_ratio > 0.6):
                        player_list_per_user.append(player)

            user_query = dict()
            user_query['user'] = user_name
            user_query['squad'] = player_list_per_user
            all_players_of_interest_for_rating_query.append(user_query)

        return all_players_of_interest_for_rating_query

    def map_players_of_interest_with_match_lineup(self, players_of_interest, match_lineup):
        """

        :param players_of_interest:
        :param match_lineup:
        :return:
        """

        print(players_of_interest)
        print("\n")
        print(match_lineup)
        for comuniouser in players_of_interest:
            user_name = comuniouser['user']
            comuniosquad = comuniouser['squad']

            for comunioplayerdata in comuniosquad:
                comunioplayername = comunioplayerdata[0]
                comunioplayername_forename, comunioplayername_surename = self.seperate_playername(playername=comunioplayername)
                #print("foren: {}, suren: {}".format(comunioplayername_forename, comunioplayername_surename))

                for homeplayer, awayplayer in zip(match_lineup['homeTeam'], match_lineup['awayTeam']):
                    homeplayer = homeplayer['player_name']
                    homeplayer_forename, homeplayer_surename = self.seperate_playername(playername=homeplayer)
                    print("foren: {}, suren: {}".format(homeplayer_forename, homeplayer_surename))
                    awayplayer = awayplayer['player_name']
                    awayplayer_forename, awayplayer_surename = self.seperate_playername(playername=awayplayer)

                    # compare comunio player name with sofascore player name



    def seperate_playername(self, playername):
        """ seperates the playername into forename and surename

        :return: forename and surename of player
        """
        playername_list = playername.split()

        if len(playername_list) == 0:
            playername_forename = ''
            playername_surename = ''
        elif len(playername_list) == 1:
            playername_forename = ''
            playername_surename = playername_list[0]
        elif len(playername_list) == 2:
            playername_forename = playername_list[0]
            playername_surename = playername_list[1]
        elif len(playername_list) == 3:
            playername_forename = playername_list[0]
            playername_surename = playername_list[2]
        else:
            playername_forename = ''
            playername_surename = ''

        return playername_forename, playername_surename

    def prepare_telegram_message(self):
        """

        :return:
        """
        pass

