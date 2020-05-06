import logging
import sqlite3
from ComunioScore.db.context import PostgresqlCursorContextManager, PostgresqlConnectionContextManager, \
    SQLiteCursorContextManager, SQLiteConnectionContextManager
from ComunioScore.exceptions import DBConnectorError
try:
    import psycopg2
    from psycopg2.pool import ThreadedConnectionPool
    from psycopg2 import Error
    is_psycopg2_importable=True
except ImportError as ex:
    is_psycopg2_importable=False
    print(ex)


class DBConnector:
    """ Base class DBConnector for connection to database

    USAGE:
            connector = DBConnector()
            connector.connect(host, port, username, password, dbname, minConn=1, maxConn=10)
    """
    # class attributes for connection and pool
    connection = None
    pool = None
    is_sqlite = False

    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class DBConnector')

    @classmethod
    def connect_psycopg(cls, host, port, username, password, dbname, minConn=1, maxConn=10):
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
            if is_psycopg2_importable:
                # create connection pool
                cls.pool = ThreadedConnectionPool(minconn=minConn, maxconn=maxConn, user=username,
                                                  password=password, host=host, port=port, database=dbname)
                logging.getLogger('ComunioScore').info("Connect to {} as user {} to database {}".format(host, username, dbname))
                return True

            else:
                print("psycogp2 is not imported")
                return False
        except psycopg2.DatabaseError as e:
            logging.getLogger('ComunioScore').error('Could not connect to ThreadedConnectionPool: {}'.format(e))
            return False

    @classmethod
    def connect_sqlite(cls, path):
        """ connection to the sqlite database

        :param path: path to database file
        """

        try:

            cls.connection = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
            cls.is_sqlite = True
            logging.getLogger('ComunioScore').info("Connect to the sqlite database at {}".format(path))
            return True

        except sqlite3.DatabaseError as ex:
            logging.getLogger('ComunioScore').error('Could not connect to sqlite Database: {}'.format(ex))
            return False

    @classmethod
    def close(cls):
        """ closes all pool connections

        """
        cls.pool.closeall()

    def get_cursor(self, autocommit=False):
        """ get a cursor object from ConnectionPool

        :param autocommit: bool to enable autocommit
        :return: cursor object
        """
        if self.pool is not None:
            return PostgresqlCursorContextManager(self.pool, autocommit=autocommit)
        elif self.connection is not None:
            return SQLiteCursorContextManager(self.connection)
        else:
            raise DBConnectorError("Database connection is not defined")

    def get_conn(self, autocommit=False):
        """ get a connection object from ConnectionPool

        :param autocommit: bool to enable autocommit
        :return: connection object
        """
        if self.pool is not None:
            return PostgresqlConnectionContextManager(self.pool, autocommit=autocommit)
        elif self.connection is not None:
            return SQLiteConnectionContextManager(self.connection)
        else:
            raise DBConnectorError("Database connection is not defined")

    def commit(self):
        """ commits a sql statement

        """
        with self.get_conn() as conn:
            conn.commit()


