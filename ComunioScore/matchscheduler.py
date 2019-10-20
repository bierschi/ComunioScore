import logging
import time
import sched


class MatchScheduler:
    """ class MatchScheduler to schedule events for matches

    USAGE:
            scheduler = MatchScheduler()
            scheduler.run()

    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('create class MatchScheduler')

        # create scheduler
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def register_events(self, timestamp, handler, prio, *args):
        """ register events to execute

        :param timestamp: start timestamp
        :param handler: handler function
        :param prio: prio for the event
        :param args: variable arguments

        :return event id
        """
        event_id = self.scheduler.enterabs(timestamp, prio, handler, argument=args)
        return event_id

    def get_event_queue(self):
        """ get current event queue

        :return: event queue
        """
        return self.scheduler.queue

    def is_queue_empty(self):
        """ is current queue empty

        :return: bool, true or false
        """
        return self.scheduler.empty()

    def cancel_event(self, eventid):
        """ cancels an event

        :param eventid: specific event id
        """
        self.scheduler.cancel(event=eventid)

    def run(self, blocking=True):
        """ runs the scheduler

        """
        self.scheduler.run(blocking=blocking)


if __name__ == '__main__':
    scheduler = MatchScheduler()
    scheduler.register_events(time.time(), 'test', 1, 'b', 'c')
    #scheduler.run()


