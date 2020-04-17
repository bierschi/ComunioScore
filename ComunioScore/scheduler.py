import logging
import heapq
import functools
import threading
from datetime import datetime


class Scheduler:
    """ class Scheduler to schedule threaded tasks

    USAGE:
            scheduler = Scheduler()
            scheduler.schedule(func, startts, *args)
    """

    @functools.total_ordering
    class _Task:
        """A scheduled task"""

        def __init__(self, func, startts, *args):
            """Create task that will run fn at or after the datetime start."""
            self.func = func
            self.start = startts
            self.args = args
            self.cancelled = False

        def __le__(self, other):
            # Tasks compare according to their start time.
            return self.start <= other.start

        @property
        def timeout(self):
            """Return time remaining in seconds before task should start."""
            return (self.start - datetime.now()).total_seconds()

        def cancel(self):
            """Cancel task if it has not already started running."""
            self.cancelled = True

    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class Scheduler')

        cv = self._cv = threading.Condition(threading.Lock())
        tasks = self._tasks = []

        def run():
            while True:
                with cv:
                    while True:
                        timeout = None
                        while tasks and tasks[0].cancelled:
                            heapq.heappop(tasks)
                        if tasks:
                            timeout = tasks[0].timeout
                            if timeout <= 0:
                                task = heapq.heappop(tasks)
                                break
                        cv.wait(timeout=timeout)
                # self.logger.info("Starting new task thread")
                threading.Thread(target=task.func, args=task.args).start()

        threading.Thread(target=run, name='Scheduler').start()

    def schedule(self, func, startts, *args):
        """Schedule a task that will run fn at or after start (which must be a
        datetime object) and return an object representing that task.

        """

        task = self._Task(functools.partial(func), startts, *args)
        with self._cv:
            heapq.heappush(self._tasks, task)
            self._cv.notify()
        return task

    def get_tasks(self):
        """ get the tasks list

        :return: list with all open tasks
        """
        return self._tasks

    def is_tasks_empty(self):
        """ checks if the tasks list is empty

        :return: True if tasks list is empty, else False
        """
        if len(self._tasks) == 0:
            return True
        else:
            return False
