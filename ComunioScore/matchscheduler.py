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

        # create the scheduler instances
        self.matchday_scheduler = Scheduler()
        self.postponed_scheduler = Scheduler()
        self.new_events_allowed = True

    @classmethod
    def register_livedata_event_handler(cls, func):
        """ registers a new livedata event handler

        :param func: event handler for the livedata method
        """
        cls.livedata_event_handler = func

    def new_event(self, event_ts, match_day, match_id, home_team, away_team, postponed=False):
        """ schedules a new match event with given match data

        :param event_ts: event start timestamp
        :param match_day: match day
        :param match_id: match id
        :param home_team: home team name
        :param away_team: away team name
        :param postponed: postponed
        """

        if self.livedata_event_handler:

            # register weekly matchday matches
            if postponed is False:
                current_tasks_len = len(self.matchday_scheduler.get_tasks())
                if current_tasks_len == 9:
                    self.new_events_allowed = False
                elif current_tasks_len < 9 and self.matchday_scheduler.is_tasks_empty():
                    self.new_events_allowed = True

                if current_tasks_len < 10 and self.new_events_allowed:
                    self.logger.info("Register new event {} for match day {}: {} vs. {}".format(match_id, match_day,
                                                                                                home_team, away_team))
                    event_ts = datetime.datetime.fromtimestamp(int(event_ts))
                    self.matchday_scheduler.schedule(self.livedata_event_handler, event_ts, match_day, match_id, home_team, away_team)
                else:
                    self.logger.error("9 match events are scheduled already. Wait...")

            # register postponed matches
            else:
                # check if the postponed match is already scheduled
                if not self.is_match_scheduled(scheduler=self.postponed_scheduler, match_id=match_id):
                    self.logger.info("Register new postponed match event {} for match day {}: {} vs. {} ".format(match_id, match_day, home_team, away_team))
                    event_ts = datetime.datetime.fromtimestamp(int(event_ts))
                    self.postponed_scheduler.schedule(self.livedata_event_handler, event_ts, match_day, match_id, home_team, away_team)
                else:
                    self.logger.error("Match event {} for match day {}: {} vs. {} is already scheduled!".format(match_id, match_day, home_team, away_team))

        else:
            self.logger.error("No livedata_event_handler configured!")

    def is_match_scheduled(self, scheduler, match_id):
        """ checks if match id is already in the scheduler task list

        :param scheduler: scheduler instance
        :param match_id: match id

        :return: True if match is already scheduled, else False
        """

        tasks = scheduler.get_tasks()

        for task in tasks:
            if task.args[1] == match_id:
                return True

        return False
