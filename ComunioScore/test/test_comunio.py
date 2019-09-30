import os
import unittest
import configparser
from ComunioScore.comunio import Comunio
from ComunioScore import ROOT_DIR


class TestComunio(unittest.TestCase):

    def setUp(self) -> None:
        # load config file
        #self.config = configparser.ConfigParser()
        #self.config.read(ROOT_DIR + '/config/cfg.ini')

        # comunio config
        #self.username = self.config.get('comunio', 'username')
        #self.password = self.config.get('comunio', 'password')

        self.comunio = Comunio()

    def test_login(self):

        login = self.comunio.login(username=os.environ['comunio_username'], password=os.environ['comunio_password'])
        self.assertTrue(login, msg="Login process for comunio failed")

    def tearDown(self) -> None:

        pass


if __name__ == '__main__':
    unittest.main()
