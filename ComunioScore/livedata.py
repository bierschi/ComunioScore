import time
import logging
import threading
from ComunioScore.db.fetcher import DBFetcher
from ComunioScore.dbagent import DBAgent
from ComunioScore.matchscheduler import MatchScheduler
from ComunioScore.score.bundesligascore import BundesligaScore


class LiveDataProvider(DBAgent):
    """ class LiveDataProvider to trigger matches for providing livedata

    USAGE:
            livedata = LiveDataProvider()
            livedata.start()

    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScoreApp')
        self.logger.info('create class LiveDataProvider')
        # init base class
        super().__init__(config_file='cfg.ini')

        # fetch data from db
        self.dbfetcher = DBFetcher()

        # register match events
        self.scheduler = MatchScheduler()

        # create run thread
        self.__thread = threading.Thread(target=self.__run)
        self.__running = False

    def __del__(self):
        pass

    def start(self, daemon=False):
        """ starts the run thread for LiveDataProvider

        """

        if self.__thread:
            if isinstance(daemon, bool):
                self.__thread.daemon = daemon
                self.__running = True
                self.logger.info("start the LiveDataProvider run thread")
                self.__thread.start()
            else:
                raise TypeError("'daemon' must be type of boolean")

    def stop(self):
        """ stops the run thread for LiveDataProvider

        """
        if self.__thread:
            self.__running = False
            self.logger.info("stop the LiveDataProvider run thread")
            self.__thread.join()

    def trigger_matches(self):
        """ triggers new match events from database

        """

        sql = "select * from comunioscore.season where match_type='notstarted' order by start_timestamp asc"
        matches = self.dbfetcher.many(sql=sql, size=9)
        #i=0
        for match in matches:
            #t = time.time() + i
            self.logger.info("register match {}".format(match[2]))
            self.scheduler.register_events(match[3], self.execute, 1, match[0], match[2], match[5], match[6])
            #i=i+3

    def execute(self, matchday, matchid, hometeam, awayteam):
        """ executes the match event

        """
        self.logger.info("Start fetching data from matchday {} with matchid {}: {}:{}".format(matchday, matchid, hometeam, awayteam))
        fetcher = LiveDataFetcher(matchid=matchid)
        fetcher.start()

    def __run(self):
        """ run thread to trigger the match events

        """

        while self.__running:
            self.logger.info("trigger matches")
            self.trigger_matches()
            while not self.scheduler.is_queue_empty():
                self.scheduler.run(blocking=False)
            time.sleep(600)  # wait 10 minutes to trigger the next match events


class LiveDataFetcher(BundesligaScore, threading.Thread):
    """ class LiveDataFetcher to fetch live data from sofascore

    USAGE:
            livefetcher = LiveDataFetcher()
            livefetcher.start()

    """
    def __init__(self, matchid):

        # init base classes
        BundesligaScore.__init__(self)
        threading.Thread.__init__(self)

        self.matchid = matchid

    def run(self):
        """ run thread for lineup rating

        """

        while not self.is_finished(matchid=self.matchid):
            #lineup = self.lineup_from_match_id(match_id=self.matchid)
            #print(lineup)
            self.logger.info("visualize lineup with rating")
            self.vis_lineup_with_rating(matchid=self.matchid)
            time.sleep(300)  # wait 10 minutes

        print("finished thread with matchid: {}".format(self.matchid))


if __name__ == '__main__':
    live = LiveDataProvider()
    live.start()
