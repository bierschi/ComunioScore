from BreachCompilationRestAPI.db.connector import DBConnector


class DBFetcher(DBConnector):
    """ class DBFetcher

    USAGE:
            fetcher = DBFetcher()
            fetcher.connect(host, port, username, password, dbname, minConn=1, maxConn=10)
            fetcher.many(sql=sql, size=20)

    """
    def __init__(self):

        # init connector base class
        super().__init__()

    def one(self, sql, autocommit=False):
        """ fetches one row from sql statement

        :param sql: sql statement
        :param autocommit: True or False

        :return: one row from table
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            cursor.execute(sql)
            return cursor.fetchone()

    def many(self, sql, size, autocommit=False):
        """ fetches many rows (size) from sql statement

        :param sql: sql statement
        :param size: size of rows
        :param autocommit: True or False

        :return: many rows from table
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            cursor.execute(sql)
            return cursor.fetchmany(size=size)

    def all(self, sql, autocommit=False):
        """

        :param sql: sql statement
        :param autocommit: True or False

        :return: all rows from table
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


if __name__ == '__main__':
    db = DBFetcher()
    db.connect(username="christian", password="", host="192.168.178.37", port="5432", dbname="")
    sql = "select * from test.\"0\" limit 500;"
    print(db.many(sql, 500))