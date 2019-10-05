import unittest
import psycopg2
from ComunioScore.db.connector import DBConnector


class TestDBConnector(unittest.TestCase):

    def setUp(self) -> None:
        host="127.0.0.1"
        port=5432
        user="postgres"
        password=""
        dbname="postgres"
        self.connector = DBConnector()
        self.connector.connect(host=host, port=port, username=user, password=password, dbname=dbname)

        pass

    def test_get_cursor(self):
        with self.connector.get_cursor() as cursor:
            self.assertIsInstance(cursor, psycopg2.extensions.cursor, msg="abc")

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
