import logging
from ComunioScore.db import DBConnector


class DBFetcher(DBConnector):
    """ class DBFetcher to fetch data from database tables

    USAGE:
            fetcher = DBFetcher()
            fetcher.connect(host, port, username, password, dbname, minConn=1, maxConn=10)
            fetcher.many(sql=sql, size=20)

    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class DBFetcher')

        # init connector base class
        super().__init__()

    def one(self, sql, data=None, autocommit=False):
        """ fetches one row from sql statement

        :param sql: sql statement
        :param data: data for sql statement
        :param autocommit: True or False

        :return: one row from table
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            if self.is_sqlite:
                sql = sql.replace('%s', '?')

            if data is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, data)
            return cursor.fetchone()

    def many(self, sql, data=None, size=None, autocommit=False):
        """ fetches many rows (size) from sql statement

        :param sql: sql statement
        :param data: data for sql statement
        :param size: size of rows
        :param autocommit: True or False

        :return: many rows from table
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            if self.is_sqlite:
                sql = sql.replace('%s', '?')

            if data is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, data)
            return cursor.fetchmany(size=size)

    def all(self, sql, data=None, autocommit=False):
        """ fetches all rows from sql statement

        :param sql: sql statement
        :param data: data for sql statement
        :param autocommit: True or False

        :return: all rows from table
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            if self.is_sqlite:
                sql = sql.replace('%s', '?')

            if data is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, data)
            return cursor.fetchall()
