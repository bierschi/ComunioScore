import os
import logging
from logging.handlers import RotatingFileHandler
from ComunioScore import ROOT_DIR


class Logger:
    """Singleton class Logger to set up a Logger instance
    USAGE:
            Logger(name='ComunioScoreApp)
    """
    __instance = None

    def __init__(self, name='CommunioScoreApp', level='info', log_folder='/var/log', log_file_size=10000000, debug=False):

        if Logger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Logger.__instance = self

        if isinstance(name, str):
            self.logger_name = name
            self.logger = logging.getLogger(name)
        else:
            raise TypeError("'name' must be type of string")

        if level == 'info':
            self.level = logging.INFO
        elif level == 'debug':
            self.level = logging.DEBUG
        elif level == 'warn':
            self.level = logging.WARN
        elif level == 'error':
            self.level = logging.ERROR
        else:
            # default level
            self.level = logging.INFO

        self.logger.setLevel(self.level)
        formatter = logging.Formatter('%(asctime)s - %(lineno)d@%(filename)s - %(levelname)s: %(message)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(formatter)

        if not debug:
            self.__create_log_folder(log_folder)
            info_log_file_path = log_folder + '/ComunioScoreApp/info.log'
            error_log_file_path = log_folder + '/ComunioScoreApp/error.log'
        else:
            if not os.path.exists(ROOT_DIR + '/logs'):
                os.mkdir(ROOT_DIR + '/logs')
            info_log_file_path = ROOT_DIR + '/logs/info.log'
            error_log_file_path = ROOT_DIR + '/logs/error.log'

        if isinstance(log_file_size, int):
            info_rotate_handler = RotatingFileHandler(info_log_file_path, mode='a', maxBytes=log_file_size, backupCount=10)  # 10mb
            info_rotate_handler.setFormatter(formatter)
            info_rotate_handler.setLevel(logging.DEBUG)  # fixed level

            error_rotate_handler = RotatingFileHandler(error_log_file_path, mode='a', maxBytes=log_file_size, backupCount=10)  # 10mb
            error_rotate_handler.setFormatter(formatter)
            error_rotate_handler.setLevel(logging.WARNING)  # fixed level
        else:
            raise TypeError("'log_file_size must be type of int!")

        self.logger.addHandler(stream_handler)
        self.logger.addHandler(info_rotate_handler)
        self.logger.addHandler(error_rotate_handler)

    @staticmethod
    def get_instance():
        """ get logger instance

        :return: Logger: logger instance
        """
        if Logger.__instance is None:
            Logger()
        return Logger.__instance

    def __create_log_folder(self, log_folder):
        """creates log folder in '/var/log/ComunioScoreApp'

        """
        try:

            if log_folder.endswith('/'):
                if not os.path.exists(log_folder + 'ComunioScoreApp'):
                    os.mkdir(log_folder + 'ComunioScoreApp')
            else:
                if not os.path.exists(log_folder + '/ComunioScoreApp'):
                    os.mkdir(log_folder + '/ComunioScoreApp')

        except PermissionError as ex:
            print("Check permission! Exception: " + str(ex))
            exit(0)

    def info(self, msg):
        """logs info messages

        :param msg: string messages
        """
        self.logger.info(msg)

    def debug(self, msg):
        """logs debug messages

        :param msg: string messages
        """
        self.logger.debug(msg)

    def warning(self, msg):
        """logs warning messages

        :param msg: string messages
        """
        self.logger.warning(msg)

    def error(self, msg):
        """logs error messages

        :param msg: string messages
        """
        self.logger.error(msg)


if __name__ == '__main__':
    logger = Logger(debug=False)
    for i in range(0, 1000):
        logger.info("test_message")
        logger.error("test_error")