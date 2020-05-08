import logging
import unicodedata
from time import sleep
from threading import Lock
from difflib import SequenceMatcher

from ComunioScore import DBHandler
from ComunioScore.score import BundesligaScore
from ComunioScore import PointCalculator


class LiveData(DBHandler):
    """ class LiveData to fetch live data from given match id

    USAGE:
            livedata = LiveData()
            livedata.fetch()

    """
    is_squad_updated = False

    def __init__(self, season_date, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class LiveData')

        # init base class
        super().__init__(**dbparams)

        # set attributes
        self.season_date = season_date
        self.running = True
        self.is_notify = True
        self.msg_rate = 10 * 60  # 10 min as default

        # bundesligascore instance
        self.bundesliga = BundesligaScore(season_date=self.season_date)

        # create PointCalculator instance
        self.pointcalculator = PointCalculator()

        # sql
        self.user_sql = "select userid, username from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_user)
        self.squad_sql = "select playername, playerposition, club  from {}.{} where userid = %s and linedup = 'true' ".format(self.comunioscore_schema, self.comunioscore_table_squad)
        self.comunio_users = self.dbfetcher.all(sql=self.user_sql)

        # event handler
        self.update_squad_event_handler = None
        self.telegram_send_event_handler = None

        # init current match day to None
        self.current_match_day = None

        # create lock object
        self.telegram_lock = Lock()

    def register_update_squad_event_handler(self, func):
        """ register the update squad event handler

        :param func: event handler
        """
        self.update_squad_event_handler = func

    def register_telegram_send_event_handler(self, func):
        """ register the telegram send event handler

        :param func: event handler
        """
        self.telegram_send_event_handler = func

    def fetch(self, match_day, match_id, home_team, away_team):
        """ fetches live data from given match id for comunio players of interest

        :param match_day: current match day
        :param match_id: match id for sofascore
        :param home_team: home team
        :param away_team: away team
        """

        live_data_start_msg = "Start fetching live data from match day {}: *{}* vs. *{}*".format(match_day, home_team, away_team)
        self.logger.info(live_data_start_msg)

        # send start msg
        if self.is_notify:
            self.telegram_lock.acquire()
            self.telegram_send_event_handler(live_data_start_msg)
            self.telegram_lock.release()

        # set current match_day
        self.current_match_day = match_day

        # update linedup comunio players in database before sending livedata
        self.update_linedup_squad()

        # collect livedata as long as match is not finished
        #while self.running:
        while self.bundesliga.is_finished(matchid=match_id):

            # get all comunio players of interest for sofascore rating
            players_of_interest_for_match = self.set_comunio_players_of_interest_for_match(home_team=home_team, away_team=away_team)

            # get match lineup from match id
            match_lineup = self.bundesliga.lineup_from_match_id(match_id=match_id)

            # create livedata with mapping of comunio players and sofascore lineup players
            self.logger.info("Map livedata for match day {}: {} vs. {}".format(match_day, home_team, away_team))
            livedata = self.map_players_of_interest_with_match_lineup(players_of_interest=players_of_interest_for_match,
                                                                      match_lineup=match_lineup)

            # calculate the points for current match day
            self.logger.info("Calculate points for match day {}: {} vs. {}".format(match_day, home_team, away_team))
            self.calculate_points_per_match(livedata=livedata, match_id=match_id, match_day=match_day)

            if self.is_notify:
                # prepare the telegram message
                self.logger.info("Prepare telegram message for match day {}: {} vs. {}".format(match_day, home_team, away_team))
                livedata_msg = self.prepare_telegram_message(livedata=livedata, home_team=home_team, away_team=away_team,
                                                             match_day=match_day, match_id=match_id)

                self.telegram_lock.acquire()
                self.telegram_send_event_handler(text=livedata_msg)
                self.telegram_lock.release()

            sleep(self.msg_rate)

        # after match is finished
        live_data_end_msg = "Finished fetching live data from match *{}* vs *{}*".format(home_team, away_team)
        self.logger.info(live_data_end_msg)

        if self.is_notify:
            # send finish msg
            self.telegram_lock.acquire()
            self.telegram_send_event_handler(text=live_data_end_msg)
            self.telegram_lock.release()

        # set linedup squad to false
        LiveData.is_squad_updated = False

    def update_linedup_squad(self):
        """ update linedup squad to fetch livedata only from linedup players

        """
        if not LiveData.is_squad_updated:
            if self.update_squad_event_handler:
                LiveData.is_squad_updated = True
                self.update_squad_event_handler()
            else:
                self.logger.error("No update_squad_event_handler registered!")
        else:
            self.logger.error("Squad already updated in LiveData class")

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

            if len(squad) < 11:
                self.logger.error("Length of linedup comunio squad from {} is less as 11".format(user_name))

            # player list of interest for one comunio user
            player_list_per_user = list()

            # check if comunio player in home or away team
            for player in squad:
                team = player[2]
                if (team == home_team) or (team == away_team):
                    player_list_per_user.append(player)
                else:
                    hometeam_ratio = SequenceMatcher(None, team, home_team).ratio()
                    awayteam_ratio = SequenceMatcher(None, team, away_team).ratio()
                    if (hometeam_ratio > 0.6) or (awayteam_ratio > 0.6):
                        player_list_per_user.append(player)

            user_query = dict()
            user_query['user'] = user_name
            user_query['userid'] = user_id
            user_query['squad'] = player_list_per_user
            all_players_of_interest_for_rating_query.append(user_query)

        return all_players_of_interest_for_rating_query

    def map_players_of_interest_with_match_lineup(self, players_of_interest, match_lineup):
        """ maps player of interest with match line up and creates a new data structure for livedata

        :param players_of_interest: players of interest
        :param match_lineup: match lineup

        :return: list with live data
        [{'user': 'Shaggy', 'userid': 13065521, 'squad': [{'name': 'Jorge Mere', 'rating': '7.6', 'position': 'defender', 'points': 6, 'incidents': [{'type': 'goal', 'class': 'regulargoal', 'player': 'Jorge Mere'}]}]}, ...]
        """

        # data with all comunio user and related players
        livedata = list()
        #print(match_lineup)
        # iterate over all comunio users
        for comuniouser in players_of_interest:
            user_name = comuniouser['user']
            user_id = comuniouser['userid']
            comuniosquad = comuniouser['squad']

            # dict with comunio user and related players for livedata
            user_squad_dict = dict()
            user_squad_dict['user'] = user_name
            user_squad_dict['userid'] = user_id
            user_squad_dict['squad'] = list()

            # iterate over squad of comunio user
            for comunioplayerdata in comuniosquad:
                comunioplayername = comunioplayerdata[0]
                comunioplayerposition = comunioplayerdata[1]
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
                                                                                     playerrating=homeplayer['player_rating'],
                                                                                     playerposition=comunioplayerposition,
                                                                                     incidents=match_lineup['homeTeamIncidents']))
                                break
                        else:
                            user_squad_dict['squad'].append(self.get_player_data(playername=homeplayer_name,
                                                                                 playerrating=homeplayer['player_rating'],
                                                                                 playerposition=comunioplayerposition,
                                                                                 incidents=match_lineup['homeTeamIncidents']))
                            break

                # iterate over all awayplayer of away team
                for awayplayer in match_lineup['awayTeam']:
                    awayplayer_name = awayplayer['player_name']
                    awayplayer_forename, awayplayer_surename = self.seperate_playername(playername=awayplayer_name)

                    #print("compare {} with {}".format(comunioplayername_surename, awayplayer_surename))

                    # compare comunio player name with sofascore player name
                    if ((comunioplayername_surename == awayplayer_surename) or
                            (SequenceMatcher(None, comunioplayername_surename, awayplayer_surename).ratio() > 0.77)):
                        if comunioplayername_forename:
                            if (comunioplayername_forename == awayplayer_forename[:len(comunioplayername_forename)]):
                                user_squad_dict['squad'].append(self.get_player_data(playername=awayplayer_name,
                                                                                     playerrating=awayplayer['player_rating'],
                                                                                     playerposition=comunioplayerposition,
                                                                                     incidents=match_lineup['awayTeamIncidents']))
                                break
                        else:
                            user_squad_dict['squad'].append(self.get_player_data(playername=awayplayer_name,
                                                                                 playerrating=awayplayer['player_rating'],
                                                                                 playerposition=comunioplayerposition,
                                                                                 incidents=match_lineup['awayTeamIncidents']))
                            break

            # add user data to list
            livedata.append(user_squad_dict)
        #print(livedata)
        return livedata

    def get_player_data(self, playername, playerrating, playerposition, incidents):
        """ get player data dict for livedata

        :param playername: player name
        :param playerrating: player rating
        :param playerposition: player position

        :return: dict of player data
        """
        player_data = dict()

        player_data['name'] = playername # from sofascore
        player_data['rating'] = playerrating
        if playerrating == "–":
            player_data['points'] = playerrating
        else:
            player_data['points'] = self.pointcalculator.get_points_from_rating(rating=float(playerrating))
        player_data['position'] = playerposition

        # check active incidents
        incidents_list = list()
        for incident in incidents:
            # check if given player has an active incident
            if incident['player'] == playername:
                # TODO remove player name incident.pop('player')
                incidents_list.append(incident)
        player_data['incidents'] = incidents_list

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

        # remove accents
        nfkd_form = unicodedata.normalize('NFKD', playername_surename)
        playername_surename_accents = u"".join([c for c in nfkd_form if not unicodedata.name(c).endswith('ACCENT')])

        return playername_forename, playername_surename_accents

    def prepare_telegram_message(self, livedata, home_team, away_team, match_day, match_id):
        """ prepares the livedata for a new telegram message

        :param livedata: livedata data structure

        :return: telegram message
        """

        telegram_str = ""
        match_str = "Points rating for *{}* vs. *{}* \n\n".format(home_team, away_team)
        telegram_str += match_str

        for user in livedata:
            username = user['user']
            userid = user['userid']
            squad = user['squad']

            telegram_str += "\n*{}*:\n".format(username)
            if len(squad) == 0:
                telegram_str += "no player in lineup!\n"
            else:
                points_data = self.query_rating_goal_off_points(userid=userid, match_day=match_day, match_id=match_id)

                points_rating = points_data[0][0]
                points_goal = points_data[0][1]
                points_off = points_data[0][2]
                points = points_rating + points_goal + points_off
                for player in squad:
                    player_str = ''.join("{} (*{}*)=>*{}*\n".format(player['name'], player['rating'], player['points']))
                    telegram_str += player_str
                rating_str = "*P: {} + G: {} + O: {} => {}*\n".format(points_rating, points_goal, points_off, points)
                telegram_str += rating_str

        return telegram_str

    def calculate_points_per_match(self, livedata, match_id, match_day):
        """ calculates the points for each user with the linedup players

        :param livedata: live data with player points
        :param match_id: match id
        :param match_day: match day

        """
        # points for rating, goals (regulargoal, penalty) and offs (YellowRed, Red)
        for user in livedata:
            userid = user['userid']
            squad = user['squad']
            points_rating = 0
            points_goals = 0
            points_offs = 0
            for player in squad:
                for incident in player['incidents']:
                    # goal points regular
                    if (incident['type'] == 'goal') and (incident['class'] == 'regulargoal'):
                        points = self.pointcalculator.get_points_for_goal(position=player['position'])
                        if points is not None:
                            points_goals += points
                    # goal points penalty
                    elif (incident['type'] == 'goal') and (incident['class'] == 'penalty'):
                        points_goals += self.pointcalculator.get_penalty()
                    # yellow red off points
                    elif (incident['type'] == 'card') and (incident['class'] == 'YellowRed'):
                        points_offs += self.pointcalculator.get_points_for_offs(off_type='yellow_red')
                    # red off points
                    elif (incident['type'] == 'card') and (incident['class'] == 'Red'):
                        points_offs += self.pointcalculator.get_points_for_offs(off_type='red')
                # rating points
                if player['points'] != '–':
                    points_rating += player['points']

            self.update_points_in_database(userid=userid, match_id=match_id, match_day=match_day,
                                           points_rating=points_rating, points_goal=points_goals, points_off=points_offs)

    def points_summery(self):
        """ sums up the current points for each comunio player

        :return: dict with sorted players and points
        """

        sum_points = dict()

        for user in self.comunio_users:
            userid = user[0]
            username = user[1]
            points_data = self.query_rating_goal_off_points(userid=userid, match_day=self.current_match_day)
            # iterate over 9 matches
            points_all = 0
            for match in points_data:
                # check if not all elements are none
                if all(el is not None for el in match):
                    points_rating = match[0]
                    points_goal = match[1]
                    points_offs = match[2]
                    points_match = points_rating + points_goal + points_offs
                    points_all += points_match
                else:
                    self.logger.error("Invalid None points: {}".format(match))
            sum_points[username] = points_all

        # sort dict by key
        sum_points_sorted = {k: v for k, v in sorted(sum_points.items(), key=lambda item: item[1], reverse=True)}

        return self.current_match_day, sum_points_sorted

    def set_msg_rate(self, rate):
        """ set the msg notification rate

        :param rate: rate
        """
        try:
            self.msg_rate = int(rate) * 60
        except ValueError as ex:
            self.logger.error(ex)

    def set_notify_flag(self, notify):
        """ sets the notify flag

        :param notify: notify flag
        """
        self.is_notify = notify
