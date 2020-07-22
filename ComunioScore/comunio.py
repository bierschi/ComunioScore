import logging
from time import sleep

from ComunioScore import ComunioRequest
from ComunioScore.exceptions import ComunioAccessTokenError


class Comunio(ComunioRequest):
    """ class Comunio to provide specific comunio data for ComunioScore

    USAGE:
            comunio = Comunio()
            if comunio.login():
                comunio.get_all_user_ids()
    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class Comunio')

        # init base class
        super().__init__()

    def login(self, username, password):
        """ login to comunio. Waits 60 seconds if login is currently not possible

        :return: bool
        """
        while not super().login(username, password):
            self.logger.error("Could not login to Comunio, wait 60s")
            sleep(60)
        return True

    def __handle_comunio_login(self):
        """ handles the comunio login

        """
        self.login(ComunioRequest.username, ComunioRequest.password)

    def get_all_user_ids(self):
        """ get the ids from all users in the community

        :return: list containing all user ids with name as dict()
                 [{'id': 14122424, 'name': 'test'}, {'id': 2421242, 'name': 'test2'}]
        """
        userids = list()

        try:
            standings_json = self.standings()

            for item_id in standings_json.get('items'):
                for user_id in standings_json['items'][item_id]['players']:
                    player_dict = dict()
                    player_dict['id'] = user_id['id']
                    player_dict['name'] = user_id['name']
                    userids.append(player_dict)
                break
            return userids

        except ComunioAccessTokenError as ex:
            self.logger.error(ex)
            self.__handle_comunio_login()
            return self.get_all_user_ids()

    def get_all_user_squads(self):
        """ get comunio users squad list

        :return: dict with id, name, squad in list
        """
        userids = self.get_all_user_ids()

        try:
            # TODO takes quite a long time, improve
            comunio_user_data = list()
            for userid in userids:
                user_data = userid
                squad = self.squad(userid=userid['id'])
                squad_list = list()
                for player in squad['items']:
                    player_dict = dict()
                    player_dict['name']     = player['name']
                    player_dict['club']     = player['club']['name']
                    player_dict['position'] = player['position']
                    player_dict['linedup']  = player['linedup']
                    squad_list.append(player_dict)
                user_data.update({'squad': squad_list})
                comunio_user_data.append(user_data)
            return comunio_user_data

        except ComunioAccessTokenError as ex:
            self.logger.error(ex)
            self.__handle_comunio_login()
            return self.get_all_user_squads()

    def get_squad(self, userid):
        """ get squad from given userid

        :param userid: int
        :return: list of players
        """

        try:
            squad = self.squad(userid=userid)
            return squad['items']

        except ComunioAccessTokenError as ex:
            self.logger.error(ex)
            self.__handle_comunio_login()
            return self.get_squad(userid=userid)

    def get_all_user_points_and_teamvalues(self):
        """ get the points and teamvalues from all comunio user within the community

        :return: dict with id, login, name, points, teamValue in list
        """
        userids = self.get_all_user_ids()

        try:
            user_data_list = list()
            for userid in userids:
                user = self.user(userid=userid['id'])

                if user['lastName']:
                    name = user['firstName'] + ' ' + user['lastName']
                else:
                    name = user['firstName']

                user_data = dict()
                user_data['id'] = user['id']
                user_data['login'] = user['login']
                user_data['name'] = name.strip()
                user_data['points'] = user['points']
                user_data['teamValue'] = user['teamValue']
                user_data_list.append(user_data)
            return user_data_list

        except ComunioAccessTokenError as ex:
            self.logger.error(ex)
            self.__handle_comunio_login()
            return self.get_all_user_points_and_teamvalues()


if __name__ == '__main__':
    com = Comunio()
    if com.login(username='', password=''):
        print(com.get_all_user_points_and_teamvalues())
