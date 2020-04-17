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
    def __init__(self, season_date, update_frequence=21600, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class SofascoreDB')

        # init base classes
        DBHandler.__init__(self, **dbparams)
        Thread.__init__(self)

        self.update_frequence = update_frequence
        self.season_date = season_date
        self.running = True
        self.update_season_counter = 0
        self.matchscheduler_event_handler = None

        # create BundesligaScore instance
        self.bundesliga = BundesligaScore(season_date=self.season_date)

    def run(self) -> None:
        """ run thread for class SofascoreDB

        """
        self.delete_season()
        sleep(1)
        self.insert_season()

        while self.running:
            sleep(300)
            self.update_season_counter += 2
            self.query_match_data()

            if self.update_season_counter > self.update_frequence:
                self.update_season()
                self.update_season_counter = 0

    def register_matchscheduler_event_handler(self, func):
        """ register the matchscheduler event handler function

        :param func: new event handler function
        """

        self.matchscheduler_event_handler = func

    def insert_season(self):
        """ insert season data into database

        """
        self.logger.info("Insert season data into database")

        sql = "insert into {}.season (match_day, match_type, match_id, start_timestamp, start_datetime, homeTeam, " \
              "awayTeam, homeScore, awayScore, season) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.comunioscore_schema)

        season_data = self.bundesliga.season_data()
        season_list = list()

        for matchday in season_data:
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

        season_data = self.bundesliga.season_data()

        sql = "update {}.season set match_type = %s, homeScore = %s, awayScore = %s where match_id = %s".format(self.comunioscore_schema)

        try:
            for matchday in season_data:
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

        last_match_day = self.get_last_match_day()
        if last_match_day is None:
            next_match_day = 1
        else:
            next_match_day = last_match_day + 1

        match_sql = "select * from {}.{} where match_day=%s".format(self.comunioscore_schema, self.comunioscore_table_season)

        match_day_data = self.dbfetcher.all(sql=match_sql, data=(next_match_day, ))
        if len(match_day_data) > 9:
            self.logger.error("length of match day data is greater than 9!!")
        else:
            if self.matchscheduler_event_handler:
                for match in match_day_data:
                    # TODO Uncomment and change 'postponed' with 'notstarted'
                    #if match[1] in ('postponed', 'canceled'):  # log postponed or canceled match types
                    #    self.logger.error("Not registering match day {}: {} vs. {} due to {}".format(match[0], match[5], match[6], match[1]))

                    if match[1] == 'postponed':  # notstarted is the normal match type for new events
                        self.matchscheduler_event_handler(event_ts=match[3], match_day=match[0], match_id=match[2], home_team=match[5], away_team=match[6])
                    else:
                        self.logger.error("Could not register new event for match day {}: {} vs. {}".format(match[0], match[5], match[6]))
            else:
                self.logger.error("No matchscheduler event handler registered!!")
