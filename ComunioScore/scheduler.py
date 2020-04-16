import logging
import time
import sched
from threading import Thread


class Scheduler(Thread):
    """ class Scheduler to schedule arbitrary events

    USAGE:
            scheduler = Scheduler()
            scheduler.start()

    """
    scheduler = sched.scheduler(time.time, time.sleep)

    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class Scheduler')

        # init base class
        super().__init__()

    def register_events(self, timestamp, handler, prio, *args):
        """ register events to execute

        :param timestamp: start timestamp
        :param handler: handler function
        :param prio: prio for the event
        :param args: variable arguments

        :return event id
        """
        return self.scheduler.enterabs(timestamp, prio, handler, argument=args)

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

    def run(self) -> None:
        """ runs the scheduler

        """

        while True:
            if not self.is_queue_empty():
                self.scheduler.run(blocking=True)
            else:
                time.sleep(2)

