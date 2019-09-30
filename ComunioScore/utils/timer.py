import logging
import threading
import functools


class PeriodicTimer:

    def __init__(self, interval, callback):
        self.logger = logging.getLogger('ComunioScoreApp')
        self.logger.info('create class PeriodicTimer')

        self.interval = interval

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            result = callback(*args, **kwargs)
            if result:
                self.thread = threading.Timer(self.interval,
                                              self.callback)
                self.thread.start()

        self.callback = wrapper

    def start(self):
        """ starts the PeriodicTimer thread

        """
        self.thread = threading.Timer(self.interval, self.callback)
        self.thread.start()

    def cancel(self):
        """  cancels the PeriodicTimer thread

        """
        self.thread.cancel()
