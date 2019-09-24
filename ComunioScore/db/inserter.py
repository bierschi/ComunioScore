from ComunioScore.db.connector import DBConnector
from ComunioScore.exceptions.db import DBInserterError


class DBInserter(DBConnector):

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
        """

        :return:
        """
        with self.get_cursor(autocommit=autocommit) as cursor:
            cursor.execute(sql, data)

    def many_rows(self, sql, datas, autocommit=False):
        """

        :return:
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

