import os
import unittest
import configparser

from ComunioScore import ComunioRequest
from ComunioScore import ROOT_DIR


class TestComunioRequest(unittest.TestCase):

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

        # create comunio request instance
        self.comrequest = ComunioRequest()
        self.test_login()

    def test_login(self):

        if self.use_env:
            login = self.comrequest.login(username=os.environ['comunio_username'], password=os.environ['comunio_password'])
        else:
            login = self.comrequest.login(username=self.username, password=self.password)
        # true means success
        self.assertTrue(login, msg="Login process for comunio failed")

    def test_get_community_name(self):

        community_name = self.comrequest.get_community_name()
        # check if community_name is string
        self.assertIsInstance(community_name, str, msg="community_name must be type of string")

    def test_get_login_userid(self):

        userid = self.comrequest.get_login_userid()
        self.assertIsInstance(userid, str, msg="userid from logged in user must be type of string")

    def test_standings(self):

        standings = self.comrequest.standings()
        # test if standing is a dict
        self.assertIsInstance(standings, dict, msg="standings must be type of dict")

    def test_squad(self):

        userid = self.comrequest.get_login_userid()
        squad = self.comrequest.squad(userid=userid)

        self.assertIsInstance(squad, dict, msg="squad must be type of dict")

    def test_squad_latest(self):

        userid = self.comrequest.get_login_userid()
        squad_latest = self.comrequest.squad_latest(userid=userid)

        self.assertIsInstance(squad_latest, dict, msg="squad latest must be type of dict")

    def test_user(self):

        userid = self.comrequest.get_login_userid()
        user = self.comrequest.user(userid=userid)

        self.assertIsInstance(user, dict, msg="user must be type of dict")

    def tearDown(self) -> None:

        self.comrequest.close()


if __name__ == '__main__':
    unittest.main()
