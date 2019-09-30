import os
import unittest
import configparser
from ComunioScore.comunio import Comunio
from ComunioScore import ROOT_DIR


class TestComunio(unittest.TestCase):

    def setUp(self) -> None:

        # load local config file
        self.config = configparser.ConfigParser()
        self.config.read(ROOT_DIR + '/config/cfg.ini')

        # for travis deployment
        self.use_env = False

        # comunio config
        try:
            self.username = self.config.get('comunio', 'username')
            self.password = self.config.get('comunio', 'password')
        except (KeyError, configparser.NoSectionError) as e:
            # for travis deployment
            self.use_env = True

        # create comunio instance
        self.comunio = Comunio()

    def test_login(self):
        if self.use_env:
            login = self.comunio.login(username=os.environ['comunio_username'], password=os.environ['comunio_password'])
        else:
            login = self.comunio.login(username=self.username, password=self.password)

        self.assertTrue(login, msg="Login process for comunio failed")

    def tearDown(self) -> None:

        pass


if __name__ == '__main__':
    unittest.main()
