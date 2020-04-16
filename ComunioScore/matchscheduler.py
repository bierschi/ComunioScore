import logging
from ComunioScore.scheduler import Scheduler


class MatchScheduler:
    """ class MatchScheduler to schedule match events

    USAGE:
            matchscheduler = MatchScheduler()
            matchscheduler.register_livedata_event_handler(func=livedata.fetch)
            matchscheduler.new_event(time.time(), 2, 103388, "team1", "team2")
    """
    livedata_event_handler = None

    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class MatchScheduler')

        # create the scheduler thread
        self.scheduler = Scheduler()
        self.scheduler.start()

    @classmethod
    def register_livedata_event_handler(cls, func):
        """ registers a new livedata event handler

        :param func: event handler for the livedata
        """
        cls.livedata_event_handler = func

    def new_event(self, event_ts, match_day, match_id, home_team, away_team):
        """ schedules a new match event with given match data

        """

        self.logger.info("Register new match event for match day {} and match id {}".format(match_day, match_id))

        if self.livedata_event_handler:
            self.scheduler.register_events(event_ts, self.livedata_event_handler, 1, match_day, match_id, home_team, away_team)
        else:
            self.logger.error("No livedata_event_handler configured!")


