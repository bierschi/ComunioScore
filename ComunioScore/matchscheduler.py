import logging
import datetime
from ComunioScore import Scheduler


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

        # create the scheduler instance
        self.scheduler = Scheduler()
        self.new_events_allowed = True

    @classmethod
    def register_livedata_event_handler(cls, func):
        """ registers a new livedata event handler

        :param func: event handler for the livedata
        """
        cls.livedata_event_handler = func

    def new_event(self, event_ts, match_day, match_id, home_team, away_team):
        """ schedules a new match event with given match data

        """

        if self.livedata_event_handler:

            current_tasks_len = len(self.scheduler.get_tasks())
            if current_tasks_len == 9:
                self.new_events_allowed = False
            elif current_tasks_len < 9 and self.scheduler.is_tasks_empty():
                self.new_events_allowed = True

            if current_tasks_len < 10 and self.new_events_allowed:
                self.logger.info("Register new event {} for match day {}: {} vs. {}".format(match_id, match_day,
                                                                                            home_team, away_team))
                event_ts = datetime.datetime.fromtimestamp(int(event_ts))
                self.scheduler.schedule(self.livedata_event_handler, event_ts, match_day, match_id, home_team, away_team)
            else:
                #self.logger.error("9 match events are scheduled already. Wait..")
                pass
        else:
            self.logger.error("No livedata_event_handler configured!")


