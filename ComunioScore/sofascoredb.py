import logging
import datetime
from threading import Thread
from time import sleep

from ComunioScore import DBHandler
from ComunioScore.score import BundesligaScore
from ComunioScore.exceptions import DBInserterError


class SofascoreDB(DBHandler, Thread):
    """ class SofascoreDB to insert sofascore data into database

    USAGE:
            sofascoredb = SofascoreDB(update_frequence=21600, **dbparams)
            sofascoredb.start()

    """
    def __init__(self, update_frequence=600, **dbparams):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class SofascoreDB')

        # init base classes
        DBHandler.__init__(self, **dbparams)
        Thread.__init__(self)

        self.update_frequence = update_frequence

        # create BundesligaScore instance
        self.bundesliga = BundesligaScore()

        self.running = True

    def run(self) -> None:
        """ run thread for class SofascoreDB

        """
        self.delete_season()
        sleep(1)
        self.insert_season()

        while self.running:
            sleep(self.update_frequence)
            self.update_season()

    def insert_season(self):
        """ insert season data into database

        """
        self.logger.info("Insert season data into database")

        sql = "insert into {}.season (match_day, match_type, match_id, start_timestamp, start_datetime, homeTeam, " \
              "awayTeam, homeScore, awayScore) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.comunioscore_schema)

        season_data = self.bundesliga.season_data()
        season_list = list()

        for matchday in season_data:
            start_dt = datetime.datetime.fromtimestamp(matchday['startTimestamp'])
            season_list.append((matchday['matchDay'], matchday['type'], matchday['matchId'], matchday['startTimestamp'],
                                start_dt,matchday['homeTeam'], matchday['awayTeam'], matchday['homeScore'], matchday['awayScore']))

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

        sql = "delete from {}.season".format(self.comunioscore_schema)

        try:
            self.dbinserter.sql(sql=sql, autocommit=True)
        except DBInserterError as ex:
            self.logger.error(ex)
