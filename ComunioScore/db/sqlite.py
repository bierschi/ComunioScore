import sqlite3
import logging
from ComunioScore.db.context import SQLiteCursorContextManager, SQLiteConnectionContextManager
from ComunioScore.exceptions import DBConnectorError


class SQLite:
    """ class SQLite for connection to sqlite database

    USAGE:
            SQLite.connect(path="database.db")

    """
    connection = None

    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info("Create class SQLite")

    def __del__(self):
        """ destructor

        """
        SQLite.connection.close()

    @classmethod
    def connect(cls, path):
        """ connects to a local database file

        :param path: path to database file
        """
        try:
            cls.connection = sqlite3.connect(path, isolation_level=None)

        except sqlite3.DatabaseError as ex:
            logging.getLogger('ComunioScore').error("Could not connect to SQLite Database: {}".format(ex))

    def get_cursor(self):
        """ get a cursor object

        :return: SQLiteCursorContextManager
        """
        if SQLite.connection is not None:
            return SQLiteCursorContextManager(conn=SQLite.connection)
        else:
            raise DBConnectorError("SQLite.connection was not defined!")

    def get_conn(self):
        """ get a connection object

        :return: SQLiteConnectionContextManager
        """
        if SQLite.connection is not None:
            return SQLiteConnectionContextManager(conn=SQLite.connection)
        else:
            raise DBConnectorError("SQLite.connection was not defined!")

    def commit(self):
        """ commits the current transaction

        """
        if SQLite.connection is not None:
            SQLite.connection.commit()
        else:
            raise DBConnectorError("SQLite.connection was not defined!")
