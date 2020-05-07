import logging
import datetime
from time import sleep
from threading import Thread

from ComunioScore import DBHandler
from ComunioScore.score import BundesligaScore
from ComunioScore.exceptions import DBInserterError


class SofascoreDB(DBHandler, Thread):
    """ class SofascoreDB to insert sofascore data into database

    USAGE:
            sofascoredb = SofascoreDB(update_frequence=21600, **dbparams)
            sofascoredb.start()

    """
    def __init__(self, season_date, update_season_frequence=21600, query_match_data_frequence=7200, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class SofascoreDB')

        # init base classes
        DBHandler.__init__(self, **dbparams)
        Thread.__init__(self)

        # attributes for the update frequence
        self.update_season_frequence = update_season_frequence        # 21600 seconds (6h)
        self.query_match_data_frequence = query_match_data_frequence  # 7200 seconds (2h)

        self.season_date = season_date
        self.running = True

        # event handler
        self.matchscheduler_event_handler = None
        self.comunio_user_data_event_handler = None

        # counters set to zero
        self.update_season_counter = 0
        self.query_match_data_counter = 0

        # create BundesligaScore instance
        self.bundesliga = BundesligaScore(season_date=self.season_date)

        self.season_data = None

    def run(self) -> None:
        """ run thread for class SofascoreDB

        """
        self.delete_season()
        sleep(1)
        self.delete_points()
        sleep(1)
        self.insert_season()
        sleep(1)
        self.insert_points()
        sleep(1)
        self.logger.info("Start sofascoredb run thread!")

        while self.running:
            sleep(1)
            self.update_season_counter += 1
            self.query_match_data_counter += 1

            if self.query_match_data_counter > self.query_match_data_frequence:
                self.query_match_data()
                self.query_match_data_counter = 0
            if self.update_season_counter > self.update_season_frequence:
                self.update_season()
                self.update_season_counter = 0

    def register_matchscheduler_event_handler(self, func):
        """ register the matchscheduler event handler function

        :param func: event handler function
        """

        self.matchscheduler_event_handler = func

    def register_comunio_user_data(self, func):
        """ register the comunio user data event handler function

        :param func: event handler function
        """
        self.comunio_user_data_event_handler = func

    def insert_season(self):
        """ insert season data into database

        """
        self.logger.info("Insert season data into database")

        sql = "insert into {}.{} (match_day, match_type, match_id, start_timestamp, start_datetime, homeTeam, " \
              "awayTeam, homeScore, awayScore, season) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
               self.comunioscore_schema, self.comunioscore_table_season)

        self.season_data = self.bundesliga.season_data()
        season_list = list()

        for matchday in self.season_data:
            start_dt = datetime.datetime.fromtimestamp(matchday['startTimestamp'])
            season_list.append((matchday['matchDay'], matchday['type'], matchday['matchId'], matchday['startTimestamp'],
                                start_dt, matchday['homeTeam'], matchday['awayTeam'], matchday['homeScore'], matchday['awayScore'], self.bundesliga.season_year))

        try:
            self.dbinserter.many_rows(sql=sql, datas=season_list)
        except DBInserterError as ex:
            self.logger.error(ex)

    def update_season(self):
        """ updates season data into database

        """
        self.logger.info("Updating season data")

        self.season_data = self.bundesliga.season_data()

        sql = "update {}.{} set match_type = %s, homeScore = %s, awayScore = %s where match_id = %s".format(
              self.comunioscore_schema, self.comunioscore_table_season)

        try:
            for matchday in self.season_data:
                self.dbinserter.row(sql=sql, data=(matchday['type'], matchday['homeScore'], matchday['awayScore'], matchday['matchId']))
        except DBInserterError as ex:
            self.logger.error(ex)

    def delete_season(self):
        """ deletes season data from database

        """
        self.logger.info("Deleting season data from database")

        sql = "delete from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_season)

        try:
            self.dbinserter.sql(sql=sql, autocommit=True)
        except DBInserterError as ex:
            self.logger.error(ex)

    def get_last_match_day(self):
        """ get last match day from database

        :return: None if first match day, else last match day
        """
        last_match_day_sql = "select match_day from {}.{} where match_type='finished' order by match_day desc limit 1"\
                             .format(self.comunioscore_schema, self.comunioscore_table_season)

        last_match_day = self.dbfetcher.one(sql=last_match_day_sql)

        if last_match_day is None:
            return None
        else:
            return last_match_day[0]

    def query_match_data(self):
        """ queries the match day data from season table and registers new match events

        """
        self.logger.info("Query match data from database")

        last_match_day = self.get_last_match_day()
        if last_match_day is None:
            next_match_day = 1
        else:
            next_match_day = last_match_day + 1

        self.logger.info("Set next_match_day to {}".format(next_match_day))

        match_sql = "select * from {}.{} where match_day=%s".format(self.comunioscore_schema, self.comunioscore_table_season)
        postponed_matches_sql = "select * from {}.{} where match_day<%s and match_type='notstarted'".format(self.comunioscore_schema, self.comunioscore_table_season)
        #next_match_day = 25
        match_day_data = self.dbfetcher.all(sql=match_sql, data=(next_match_day, ))
        postponed_matches_data = self.dbfetcher.all(sql=postponed_matches_sql, data=(next_match_day, ))

        if len(match_day_data) > 18:
            self.logger.error("length of match day data is greater than 18!! Length: {}".format(len(match_day_data)))
        else:
            if self.matchscheduler_event_handler:
                # register weekly matchday data
                self.logger.info("Start registering {} matches for match day {}".format(len(match_day_data), next_match_day))
                for (i, match) in enumerate(match_day_data):
                    # TODO Uncomment and change 'postponed' with 'notstarted'
                    if match[1] in ('postponed', 'canceled'):  # log postponed or canceled match types
                        self.logger.error("Not registering match day {}: {} vs. {} because match is {}".format(match[0], match[5], match[6], match[1]))

                    elif match[1] == 'notstarted':  # notstarted is the normal match type for new events
                        self.matchscheduler_event_handler(event_ts=match[3], match_day=match[0], match_id=match[2], home_team=match[5], away_team=match[6])
                    else:
                        self.logger.error("Could not register new event for match day {} ({}): {} vs. {}".format(match[0], match[1], match[5], match[6]))

                self.logger.info("Finished registering matches for match day {}".format(next_match_day))

                # register postponed matches data
                for (i, match) in enumerate(postponed_matches_data):
                    self.matchscheduler_event_handler(event_ts=match[3], match_day=match[0], match_id=match[2], home_team=match[5], away_team=match[6], postponed=True)
            else:
                self.logger.error("No matchscheduler event handler registered!!")

    def insert_points(self):
        """ inserts all data into points table

        """
        self.logger.info("Insert points data into database")

        points_sql = "insert into {}.{} (userid, username, match_id, match_day, hometeam, awayteam) " \
                     "values (%s, %s, %s, %s, %s, %s)".format(self.comunioscore_schema, self.comunioscore_table_points)

        points_table_list = list()
        if self.comunio_user_data_event_handler:
            player_standing = self.comunio_user_data_event_handler()
            for player in player_standing:
                userid = player['id']
                username = player['name'].strip()
                for matchday in self.season_data:
                    points_table_list.append((userid, username, matchday['matchId'], matchday['matchDay'], matchday['homeTeam'], matchday['awayTeam']))

            try:
                self.dbinserter.many_rows(sql=points_sql, datas=points_table_list)
            except DBInserterError as ex:
                self.logger.error(ex)
        else:
            self.logger.error("Event Handler for comunio user data is None!")

    def delete_points(self):
        """ deletes all data from points table

        """
        self.logger.info("Deleting points data from database")

        sql = "delete from {}.{}".format(self.comunioscore_schema, self.comunioscore_table_points)

        try:
            self.dbinserter.sql(sql=sql, autocommit=True)
        except DBInserterError as ex:
            self.logger.error(ex)
