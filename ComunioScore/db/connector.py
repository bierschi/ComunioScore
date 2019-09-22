import psycopg2
from psycopg2.pool import ThreadedConnectionPool

from BreachCompilationRestAPI.db.context import CursorContextManager, ConnectionContextManager
from BreachCompilationRestAPI.exceptions.db import DBConnectorError


class DBConnector:
    """ Base class DBConnector for connection to database

    USAGE:
            connector = DBConnector()
            connector.connect(host, port, username, password, dbname, minConn=1, maxConn=10)
    """
    def __init__(self):

        # attribute for connection pools
        self.pool = None

    def connect(self, host, port, username, password, dbname, minConn=1, maxConn=10):
        """ connect to ThreadedConnectionPool

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
            self.pool = ThreadedConnectionPool(minconn=minConn, maxconn=maxConn, user=username,
                                               password=password, host=host, port=port, database=dbname)
        except psycopg2.DatabaseError as e:
            print(e)

    def get_cursor(self, autocommit=False):
        """ get a cursor object from ConnectionPool

        :return: cursor object
        """
        if self.pool is not None:
            return CursorContextManager(self.pool, autocommit=autocommit)
        else:
            raise DBConnectorError("ThreadedConnectionPool was not defined")

    def get_conn(self, autocommit=False):
        """ get a connection object from ConnectionPool

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
