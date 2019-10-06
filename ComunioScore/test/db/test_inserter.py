import unittest
from ComunioScore.db.inserter import DBInserter


class TestDBInserter(unittest.TestCase):

    def setUp(self) -> None:

        self.inserter = DBInserter()
        self.inserter.connect(host="127.0.0.1", port=5432, username="postgres", password="", dbname="postgres")

    def test_sql(self):
        pass

    def test_row(self):
        pass

    def test_many_rows(self):
        pass

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
