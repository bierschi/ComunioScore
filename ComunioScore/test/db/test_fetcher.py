import unittest
from ComunioScore.db.fetcher import DBFetcher
from ComunioScore.db.inserter import DBInserter
from ComunioScore.db.creator import DBCreator, Table, Column
from ComunioScore.db.connector import DBConnector


class TestDBFetcher(unittest.TestCase):

    def setUp(self) -> None:

        # set up DBConnector instance

        DBConnector().connect(host="127.0.0.1", port=5432, username="postgres", password="", dbname="postgres")
        self.fetcher = DBFetcher()
        self.inserter = DBInserter()
        self.creator = DBCreator()
        self.creator.build(obj=Table("test", Column(name="id", type="bigint"),
                                             Column(name="username", type="text")))

        sql = "insert into test (id, username) values (%s, %s)"
        self.inserter.many_rows(sql=sql, datas=[(0, "abc"), (1, "def"), (2, "ghi")])

    def test_one(self):

        sql = "select * from test"
        one_row = self.fetcher.one(sql=sql)
        self.assertIsInstance(one_row, tuple, msg="one row must be of type tuple")
        self.assertEqual(one_row[0], 0, msg="first element in one_row must be 0")
        self.assertEqual(one_row[1], 'abc', msg="second element in one_row must be 'abc'")

    def test_many(self):
        pass

    def test_all(self):
        pass

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
