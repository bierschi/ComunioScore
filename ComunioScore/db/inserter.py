from ComunioScore.db.connector import DBConnector
from ComunioScore.exceptions.db import DBInserterError


class DBInserter(DBConnector):
    """ class DBInserter to insert data into the database

    USAGE:
            inserter = DBInserter()
            inserter.connect(host, port, username, password, dbname, minConn=1, maxConn=10)
            inserter.row(sql=sql, data=(3, "test", 5))

    """
    def __init__(self):

        # init connector base class
        super().__init__()

        pass

    def one(self):
        """

        :return:
        """
        pass

    def row(self, sql, data, autocommit=False):
        """ insert one row into database table

                sql= INSERT INTO comunio (id, username, wealth) VALUES (%s, %s, %s)
                data = (13, "test", 353.24)

                row(sql=sql, data=data)
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            cursor.execute(sql, data)

    def many_rows(self, sql, datas, autocommit=False):
        """ insert many rows into database table

                sql= INSERT INTO comunio (id, username, wealth) VALUES (%s, %s, %s)
                datas = [(13, "test", 353.24), (14, "test2", 400.02)]

                many_rows(sql=sql, datas=datas)
        """
        if isinstance(datas, list):
            with self.get_cursor(autocommit=autocommit) as cursor:
                cursor.executemany(sql, datas)
        else:
            raise DBInserterError("'datas' must be type of list")


if __name__ == '__main__':
    inserter = DBInserter()
    inserter.connect(host="192.168.178.37", port=5432, username="", password="", dbname="test")
    sql="INSERT INTO comunio (username, id, wealth) VALUES (%s, %s, %s)"
    inserter.many_rows(sql, datas=[("abcdef", 13, 353.23)], autocommit=False)

