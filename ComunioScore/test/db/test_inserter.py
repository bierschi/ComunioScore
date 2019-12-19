import unittest
from ComunioScore.db.fetcher import DBFetcher
from ComunioScore.db.inserter import DBInserter
from ComunioScore.db.creator import DBCreator, Table, Column
from ComunioScore.db.connector import DBConnector


class TestDBInserter(unittest.TestCase):

    def setUp(self) -> None:

        # set up DBConnector instance
        DBConnector().connect_psycopg(host="127.0.0.1", port=5432, username="postgres", password="postgres", dbname="postgres")
        self.fetcher = DBFetcher()
        self.inserter = DBInserter()
        self.creator = DBCreator()
        self.creator.build(obj=Table("test", Column(name="id", type="bigint"),
                                             Column(name="username", type="text")))

    def test_sql(self):
        pass

    def test_row(self):

        sql = "insert into test (id, username) values (%s, %s)"
        self.inserter.row(sql=sql, data=(0, "abc"))
        sql_fetch = "select * from test"
        one_row = self.fetcher.one(sql=sql_fetch)
        self.assertIsInstance(one_row, tuple, msg="one row must be of type tuple")
        self.assertEqual(one_row[0], 0, msg="first element in one_row must be 0")
        self.assertEqual(one_row[1], 'abc', msg="second element in one_row must be 'abc'")

    def test_many_rows(self):

        sql = "insert into test (id, username) values (%s, %s)"
        self.inserter.many_rows(sql=sql, datas=[(0, "abc"), (1, "def"), (2, "ghi")])

        sql_fetch = "select * from test"
        rows = self.fetcher.many(sql=sql_fetch, size=3)
        self.assertIsInstance(rows, list, msg="rows must be of type tuple")
        self.assertEqual(len(rows), 3, msg="rows must be of length 2")

    def tearDown(self) -> None:

        sql = "delete from test"
        self.inserter.sql(sql=sql)


if __name__ == '__main__':
    unittest.main()
