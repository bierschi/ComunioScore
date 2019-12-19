import unittest
import psycopg2
from ComunioScore.db.connector import DBConnector


class TestDBConnector(unittest.TestCase):

    def setUp(self) -> None:

        # set up DBConnector instance
        self.connector = DBConnector()
        self.connector.connect_psycopg(host="127.0.0.1", port=5432, username="postgres", password="postgres", dbname="postgres")

    def test_get_cursor(self):

        with self.connector.get_cursor() as cursor:
            self.assertIsInstance(cursor, psycopg2.extensions.cursor, msg="cursor must be type of psycopg2.extensions.cursor")

    def test_get_conn(self):

        with self.connector.get_conn() as conn:
            self.assertIsInstance(conn, psycopg2.extensions.connection, msg="conn must be type of psycopg2.extensions.connection")

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
