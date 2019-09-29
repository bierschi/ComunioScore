import logging
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

from ComunioScore.db.context import CursorContextManager, ConnectionContextManager
from ComunioScore.exceptions.db import DBConnectorError


class DBConnector:
    """ Base class DBConnector for connection to database

    USAGE:
            connector = DBConnector()
            connector.connect(host, port, username, password, dbname, minConn=1, maxConn=10)
    """
    # attribute for connection pools
    pool = None

    def __init__(self):
        self.logger = logging.getLogger('ComunioScoreApp')
        self.logger.info('create class DBConnector')

    @classmethod
    def connect(cls, host, port, username, password, dbname, minConn=1, maxConn=10):
        """ connection to the ThreadedConnectionPool

        :param host: hostname of database
        :param port: port of database
        :param username: username for connection
        :param password: password for connection
        :param dbname: database name for connection
        :param minConn: minimum connections
        :param maxConn: maximum connections
        """
        try:
            # create connection pool
            cls.pool = ThreadedConnectionPool(minconn=minConn, maxconn=maxConn, user=username,
                                               password=password, host=host, port=port, database=dbname)

        except psycopg2.DatabaseError as e:
            logging.getLogger('ComunioScoreApp').error('Could not connect to ThreadedConnectionPool: {}'.format(e))

    def get_cursor(self, autocommit=False):
        """ get a cursor object from ConnectionPool

        :param autocommit: bool to enable autocommit
        :return: cursor object
        """
        if self.pool is not None:
            return CursorContextManager(self.pool, autocommit=autocommit)
        else:
            raise DBConnectorError("ThreadedConnectionPool was not defined")

    def get_conn(self, autocommit=False):
        """ get a connection object from ConnectionPool

        :param autocommit: bool to enable autocommit
        :return: connection object
        """
        if self.pool is not None:
            return ConnectionContextManager(self.pool, autocommit=autocommit)
        else:
            raise DBConnectorError("ThreadedConnectionPool was not defined")

    def commit(self):
        """ commits a sql statement

        """
        if self.pool is not None:
            with self.get_conn() as conn:
                conn.commit()
        else:
            raise DBConnectorError("ThreadedConnectionPool was not defined")
