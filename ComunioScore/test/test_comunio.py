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

        # login to comunio
        self.test_login()

    def test_login(self):
        if self.use_env:
            login = self.comunio.login(username=os.environ['comunio_username'], password=os.environ['comunio_password'])
        else:
            login = self.comunio.login(username=self.username, password=self.password)
        # true means success
        self.assertTrue(login, msg="Login process for comunio failed")

    def test_get_all_user_ids(self):

        user_ids = self.comunio.get_all_user_ids()

        # test if user_ids is list
        self.assertIsInstance(user_ids, list, msg="user_ids must be type of list")

        for user in user_ids:
            # test if dictionary
            self.assertIsInstance(user, dict, msg="user in user_ids must be type of dict")
            # check key 'id'
            self.assertIn('id', user, msg="'id' not in user dict")
            # check key 'name'
            self.assertIn('name', user, msg="'name' not in user dict")

    def test_get_all_user_squads(self):

        user_squads = self.comunio.get_all_user_squads()
        self.assertIsInstance(user_squads, list, msg="user_squads must be type of list")

        for user in user_squads:
            self.assertIsInstance(user, dict, msg='')
            self.assertIn('id', user, msg='user in user_squads has no key id')
            self.assertIn('name', user, msg='user in user_squads has no key name')
            self.assertIn('squad', user, msg='user in user_squads has no key squad')

            for player in user['squad']:
                self.assertIsInstance(player, dict, msg="player in user[squad] must be type of dict")
                self.assertIn('name', player, msg="player has no key name")
                self.assertIn('club', player, msg="player has no key club")
                self.assertIn('position', player, msg="player has no key position")
                self.assertIn('linedup', player, msg="player has no key linedup")

    def test_get_squad(self):

        user_id = self.comunio.get_login_userid()
        squad = self.comunio.get_squad(userid=user_id)

        # check if squad is list
        self.assertIsInstance(squad, list, msg="'squad' must be type of list")

        for player in squad:
            # check dict and dict keys
            self.assertIsInstance(player, dict, msg='player within squad list must be type of dict')
            self.assertIn('id', player, msg='player dict has no key id')
            self.assertIn('name', player, msg='player dict has no key name')
            self.assertIn('club', player, msg='player dict has no key club')

    def test_get_all_user_points_and_teamvalues(self):

        user_points_teamvalues = self.comunio.get_all_user_points_and_teamvalues()

        # check if user_data is list
        self.assertIsInstance(user_points_teamvalues, list, msg="user_points_teamvalues must be type of list")

        for user in user_points_teamvalues:
            # check if user is dict and dict keys
            self.assertIsInstance(user, dict, msg="user in user_points_teamvalues must be type of dict")
            self.assertIn('id', user, msg="user in user_points_teamvalues has no key id")
            self.assertIn('login', user, msg="user in user_points_teamvalues has no key login")
            self.assertIn('name', user, msg="user in user_points_teamvalues has no key name")
            self.assertIn('points', user, msg="user in user_points_teamvalues has no key points")
            self.assertIn('teamValue', user, msg="user in user_points_teamvalues has no key teamValue")

    def tearDown(self) -> None:
        self.comunio.close()


if __name__ == '__main__':
    unittest.main()
