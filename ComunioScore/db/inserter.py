import logging
from ComunioScore.db import DBConnector, Error
from ComunioScore.exceptions import DBInserterError, DBIntegrityError


class DBInserter(DBConnector):
    """ class DBInserter to insert data into the database

    USAGE:
            inserter = DBInserter()
            inserter.connect(host, port, username, password, dbname, minConn=1, maxConn=10)
            inserter.row(sql=sql, data=(3, "test", 5))

    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class DBInserter')

        # init connector base class
        super().__init__()

    def sql(self, sql, autocommit=False):
        """ executes a sql statement

        :param sql: sql statement
        :param autocommit: bool to enable autocommit
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            cursor.execute(sql)

    def one(self):
        """ insert one entry in a row

        """
        pass

    def row(self, sql, data, autocommit=False):
        """ insert one row into database table

                sql= INSERT INTO comunio (id, username, wealth) VALUES (%s, %s, %s)
                data = (13, "test", 353.24)

                row(sql=sql, data=data)

        :param sql: sql statement
        :param data: data as a set
        :param autocommit: bool to enable autocommit
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            if self.is_sqlite:
                sql = sql.replace('%s', '?')
            try:
                cursor.execute(sql, data)
            except Error as e:
                if e.pgcode == '23505':

                    raise DBIntegrityError(e)

    def many_rows(self, sql, datas, autocommit=False):
        """ insert many rows into database table

                sql= INSERT INTO comunio (id, username, wealth) VALUES (%s, %s, %s)
                datas = [(13, "test", 353.24), (14, "test2", 400.02)]

                many_rows(sql=sql, datas=datas)

        :param sql: sql statement
        :param datas: data as a list
        :param autocommit: bool to enable autocomm
        """
        if isinstance(datas, list):
            with self.get_cursor(autocommit=autocommit) as cursor:
                if self.is_sqlite:
                    sql = sql.replace('%s', '?')
                try:
                    cursor.executemany(sql, datas)
                except Error as e:
                    if e.pgcode == '23505':
                        raise DBIntegrityError(e)
        else:
            raise DBInserterError("'datas' must be type of list")


