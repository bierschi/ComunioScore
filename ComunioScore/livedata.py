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

        # while not finished
        for i in range(0, 3):
            # get all comunio players of interest for sofascore rating
            players_of_interest_for_match = self.set_comunio_players_of_interest_for_match(home_team=home_team, away_team=away_team)

            # get match lineup from match id
            match_lineup = self.bundesliga.lineup_from_match_id(match_id=match_id)

            # create livedata with mapping of comunio players and sofascore lineup players
            livedata = self.map_players_of_interest_with_match_lineup(players_of_interest=players_of_interest_for_match,
                                                                      match_lineup=match_lineup)

            livedata_msg = self.prepare_telegram_message(livedata=livedata, home_team=home_team, away_team=away_team)
            self.telegram.new_msg(text=livedata_msg)

            sleep(random.randint(0, 20))

        # 1. get players from home team and away team of given match id
        # 2. check squad from each comunio user if a player in home or away team
        # 3. create new data structure for the relevant players
        # 4. request the current rating of the relevant players
        # 5. send telegram message periodically or with an command handler
        # 6. when match is finished, calculate points from player rating with cards and goals

        live_data_end_msg = "Finished fetching live data from match *{}* vs *{}*".format(home_team, away_team)
        self.logger.info(live_data_end_msg)
        self.telegram.new_msg(text=live_data_end_msg)

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
        """ maps player of interest with match line up and creates a new data structure for livedata

        :param players_of_interest: players of interest
        :param match_lineup: match lineup

        :return: dict with live data
        """

        # data with all comunio user and related players
        livedata = list()

        # iterate over all comunio users
        for comuniouser in players_of_interest:
            user_name = comuniouser['user']
            comuniosquad = comuniouser['squad']

            # dict with comunio user and related players for livedata
            user_squad_dict = dict()
            user_squad_dict['user'] = user_name
            user_squad_dict['squad'] = list()

            # iterate over squad of comunio user
            for comunioplayerdata in comuniosquad:
                comunioplayername = comunioplayerdata[0]
                comunioplayername_forename, comunioplayername_surename = self.seperate_playername(playername=comunioplayername)

                # iterate over all homeplayer of home team
                for homeplayer in match_lineup['homeTeam']:
                    homeplayer_name = homeplayer['player_name']
                    homeplayer_forename, homeplayer_surename = self.seperate_playername(playername=homeplayer_name)

                    #print("compare {} with {}".format(comunioplayername_surename, homeplayer_surename))

                    # compare comunio player name with sofascore player name
                    if ((comunioplayername_surename == homeplayer_surename) or
                            (SequenceMatcher(None, comunioplayername_surename, homeplayer_surename,).ratio() > 0.74)):
                        if comunioplayername_forename:
                            if comunioplayername_forename == homeplayer_forename[:len(comunioplayername_forename)]:
                                user_squad_dict['squad'].append(self.get_player_data(playername=homeplayer_name,
                                                                                     playerrating=homeplayer['player_rating']))
                                break
                        else:
                            user_squad_dict['squad'].append(self.get_player_data(playername=homeplayer_name,
                                                                                 playerrating=homeplayer['player_rating']))
                            break

                # iterate over all awayplayer of away team
                for awayplayer in match_lineup['awayTeam']:
                    awayplayer_name = awayplayer['player_name']
                    awayplayer_forename, awayplayer_surename = self.seperate_playername(playername=awayplayer_name)

                    #print("compare {} with {}".format(comunioplayername_surename, awayplayer_surename))

                    # compare comunio player name with sofascore player name
                    if ((comunioplayername_surename == awayplayer_surename) or
                            (SequenceMatcher(None, comunioplayername_surename, awayplayer_surename).ratio() > 0.74)):
                        if comunioplayername_forename:
                            if (comunioplayername_forename == awayplayer_forename[:len(comunioplayername_forename)]):
                                user_squad_dict['squad'].append(self.get_player_data(playername=awayplayer_name,
                                                                                     playerrating=awayplayer['player_rating']))
                                break
                        else:
                            user_squad_dict['squad'].append(self.get_player_data(playername=awayplayer_name,
                                                                                 playerrating=awayplayer['player_rating']))
                            break

            # add user data to list
            livedata.append(user_squad_dict)

        return livedata

    def get_player_data(self, playername, playerrating):
        """ get player data dict for livedata

        :param playername: player name
        :param playerrating: player rating

        :return: dict of player data
        """
        player_data = dict()
        player_data['name'] = playername
        player_data['rating'] = playerrating

        return player_data

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
            playername_forename = playername_list[0].replace('.', '')
            playername_surename = playername_list[1]
        elif len(playername_list) == 3:
            playername_forename = playername_list[0]
            playername_surename = playername_list[2]
        else:
            playername_forename = ''
            playername_surename = ''

        return playername_forename, playername_surename

    def prepare_telegram_message(self, livedata, home_team, away_team):
        """ prepares the livedata for a new telegram message

        :param livedata: livedata data structure

        :return: telegram message
        """

        telegram_str = ""
        match_str = "Player rating for *{}* vs. *{}* \n\n".format(home_team, away_team)
        telegram_str += match_str
        for user in livedata:
            username = user['user']
            squad = user['squad']
            telegram_str += "\n*{}*:\n".format(username)
            if len(squad) == 0:
                telegram_str += "no player!\n"
            else:
                for player in squad:
                    player_str = ''.join("{} (*{}*)\n".format(player['name'], player['rating']))
                    telegram_str += player_str
        #print(telegram_str)
        # TODO Calculate current points of players
        return telegram_str
