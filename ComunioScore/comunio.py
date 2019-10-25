import json
import logging
import requests


class Comunio:
    """ class Comunio to request data from logged in community

    USAGE:
            comunio = Comunio()
            comunio.login(username='', password='')
            comunio.get_all_user_ids()
    """
    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('create class Comunio')

        # user
        self.username = ''
        self.password = ''
        self.userid = ''                    # userid of logged in user
        self.leader = False
        self.user_budget = ''
        self.user_teamvalue = ''

        # community
        self.communityid = ''               # id of community from logged in user
        self.communityname = ''             # name of community

        self.userids = list()               # list of all userids in community of logged in user
        self.placement_and_userids = []     # dict with userid as key and placement as value
        self.last_matchday = ''

        # HTTP Header parameters
        self.session = requests.Session()
        self.auth_token = None                # authtoken to perform http request as a logged in user
        self.auth_token_expires = ''
        self.auth_info = None
        self.origin = 'http://www.comunio.de'
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/60.0.3112.78 Chrome/60.0.3112.78 Safari/537.36'
        self.accept_encoding = 'gzip, deflate, br'
        self.connection = 'keep-alive'

        self.headers_login = {
            'Origin': self.origin,
            'Accept-Encoding': self.accept_encoding,
            'Accept-Language': 'de-DE,en-EN;q=0.9',
            'User-Agent': self.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'http://www.comunio.de/home',
            'Connection': self.connection,
        }

    def __del__(self):
        """ destructor

        """
        self.session.close()
        if self.auth_token is not None:
            self.session.cookies.clear()

    def login(self, username, password):
        """ comunio login with username and password

        :param username: username of account
        :param password: password of account
        :return: bool, if login was successful
        """

        data_login = [('username', username), ('password', password),]

        try:

            request_login = self.session.post('https://api.comunio.de/login', headers=self.headers_login, data=data_login)

        except requests.exceptions.RequestException as e:
            self.logger.error("Got RequestException: {}".format(e))
            return False

        if request_login.status_code == 400:
            error_data = json.loads(request_login.text)
            self.logger.error(error_data)
            return False
        elif not request_login.status_code // 100 == 2:
            error_data = json.loads(request_login.text)
            self.logger.error(error_data)
            return False

        json_data = json.loads(request_login.text)
        self.auth_token = str(json_data['access_token'])
        self.auth_token_expires = str(json_data['expires_in'])
        self.auth_info = json_data
        if self.__set_user_and_community_info() != 200:
            self.logger.error("failed to set user and community attributes")
            raise AttributeError("failed to set user and community attributes")

        return True

    def __set_user_and_community_info(self):
        """ sets user and community specific attributes

        :return: response code from request
        """

        headers_info = {
            'Origin': self.origin,
            'Accept-Encoding': self.accept_encoding,
            'Accept-Language': 'en-EN',
            'Authorization': 'Bearer ' + self.auth_token,
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'http://www.comunio.de/dashboard',
            'User-Agent': self.user_agent,
            'Connection': self.connection,
        }
        request_info = requests.get('https://api.comunio.de/', headers=headers_info)
        json_data = json.loads(request_info.text)

        self.username = json_data['user']['name']
        self.userid = json_data['user']['id']
        self.leader = json_data['user']['isLeader']
        self.user_budget = json_data['user']['budget']
        self.user_teamvalue = json_data['user']['teamValue']
        self.communityname = json_data['community']['name']
        self.communityid = json_data['community']['id']

        return request_info.status_code

    def get_auth_info(self):
        """ get the auth infos from login process

        :return: auth_info as json dict
        """
        if self.auth_token is not None:
            return self.auth_info

    def get_all_user_ids(self):
        """ get all user ids in community

        :return: list containing all user ids with name as dict()
        """
        if self.auth_token is not None:
            headers_standings = {
                'Origin': self.origin,
                'Accept-Encoding': self.accept_encoding,
                'Accept-Language': 'de-DE,en-EN;q=0.9',
                'Authorization': 'Bearer ' + self.auth_token,
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'http://www.comunio.de/standings/total',
                'User-Agent': self.user_agent,
                'Connection': self.connection,
            }

            params_standings = (('period', 'season'),)
            request_standing = requests.get('https://api.comunio.de/communities/' + self.communityid +
                                           '/standings', headers=headers_standings, params=params_standings)

            json_data = json.loads(request_standing.text)

            tempid = ''
            # workaround to get id of object that stores all user ids
            for id in json_data.get('items'):
                tempid = id
            for id in json_data['items'][tempid]['players']:
                player_dict = dict()
                player_dict['id'] = id['id']
                player_dict['name'] = id['name']
                self.userids.append(player_dict)

            return self.userids
        else:
            pass

    def get_player_standings(self):
        """ get the player standings

        :return: list with dicts of player standings
        """
        if self.auth_token is not None:
            headers_standings = {
                'Origin': self.origin,
                'Accept-Encoding': self.accept_encoding,
                'Accept-Language': 'de-DE,en-EN;q=0.9',
                'Authorization': 'Bearer ' + self.auth_token,
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'http://www.comunio.de/standings/total',
                'User-Agent': self.user_agent,
                'Connection': self.connection,
            }

            params_standings = (('period', 'season'),)
            request_standing = requests.get('https://api.comunio.de/communities/' + self.communityid +
                                           '/standings', headers=headers_standings, params=params_standings)

            json_data = json.loads(request_standing.text)
            tempid = ''
            # workaround to get id of object that stores all user ids
            for id in json_data.get('items'):
                tempid = id

            return json_data['items'][tempid]['players']
        else:
            pass

    def set_auth_token(self, auth_token):
        """ sets the auth token

        """
        self.auth_token = auth_token

    def get_auth_token(self):
        """ get auth token

        :return: auth_token as string
        """
        if self.auth_token is not None:
            return self.auth_token

    def get_auth_expire_time(self):
        """ get auth token expire time

        :return: string, auth token expire time
        """
        if self.auth_token is not None:
            return self.auth_token_expires

    def get_user_id(self):
        """ get user id from logged in user

        :return: userid as string
        """
        if self.auth_token is not None:
            return self.userid

    def get_community_id(self):
        """ get community id from logged in user

        :return: communityid as string
        """
        if self.auth_token is not None:
            return self.communityid

    def get_community_name(self):
        """ get community name from logged in user

        :return: community name as string
        """
        if self.auth_token is not None:
            return self.communityname

    def get_wealth(self, userid):
        """ get wealth from given userid

        :param userid: int number
        :return: wealth as int number
        """
        if self.auth_token is not None:
            headers_info = {
                'Origin': self.origin,
                'Accept-Encoding': self.accept_encoding,
                'Accept-Language': 'en-EN',
                'Authorization': 'Bearer ' + self.auth_token,
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'http://www.comunio.de/standings/total',
                'User-Agent': self.user_agent,
                'Connection': self.connection,
            }

            request_info = requests.get('https://api.comunio.de/users/' + str(userid) + '/squad-latest', headers=headers_info)
            json_data = json.loads(request_info.text)
            wealth = json_data['matchday']['budget']
            if wealth is None:  # no budget available
                return wealth
            else:
                return int(json_data['matchday']['budget'])

    def get_squad(self, userid):
        """ get squad from given userid

        :param userid: int number
        :return: list, containing the squad as dict
        """
        if self.auth_token is not None:
            header = {
                'Origin': self.origin,
                'Accept-Encoding': self.accept_encoding,
                'Accept-Language': 'en-EN',
                'Authorization': 'Bearer ' + self.auth_token,
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': self.user_agent,
                'Connection': self.connection,
            }

            squad_request = requests.get('https://api.comunio.de/users/' + str(userid) + '/squad', headers=header)

            json_data = squad_request.json()
            return json_data['items']

    def get_comunio_user_data(self):
        """ get comunio user data -> id, name, squad

        :return: dict with id, name, squad in list
        """
        if self.auth_token is not None:
            users = self.get_all_user_ids()
            comunio_user_data = list()
            for user in users:
                user_data = user.copy()
                squad = self.get_squad(user['id'])
                squad_list = list()
                for player in squad:
                    player_dict = dict()
                    player_dict['name']     = player['name']
                    player_dict['club']     = player['club']['name']
                    player_dict['position'] = player['position']
                    squad_list.append(player_dict)
                user_data.update({'squad': squad_list})
                comunio_user_data.append(user_data)

            return comunio_user_data

        else:
            pass


if __name__ == '__main__':
    comunio = Comunio()
    print(comunio.login(username='', password=''))
    print(comunio.get_wealth(comunio.get_user_id()))


