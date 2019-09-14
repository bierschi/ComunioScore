import os
import json
import requests


class Comunio:

    def __init__(self):
        # user
        self.username = ''
        self.password = ''
        self.userid = ''                    # userid of logged in user
        self.leader = False
        self.user_budget = ''
        self.user_teamvalue = ''

        # comunity
        self.communityid = ''               # id of community from logged in user
        self.comunityname = ''              # name of community

        self.userids = list()               # list of all userids in community of logged in user
        self.placement_and_userids = []     # dict with userid as key and placement as value
        self.last_matchday = ''

        # HTTP Header parameters
        self.session = requests.Session()
        self.auth_token = ''                # authtoken to perform http request as a logged in user
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

    def login(self, username, password):
        """

        :param username:
        :param password:
        :return:
        """

        data_login = [('username', username), ('password', password),]

        try:
            request_login = self.session.post('https://api.comunio.de/login', headers=self.headers_login, data=data_login)

            if not request_login.status_code // 100 == 2:
                error_data = json.loads(request_login.text)
                error_text = error_data['error_description']
                return error_text

            json_data = json.loads(request_login.text)

            self.auth_token = str(json_data['access_token'])
            if self.__set_user_and_community_info() != 200:
                raise AttributeError("failed to set user and community attributes")

            return self.auth_token

        except requests.exceptions.RequestException as e:
            print(e)

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
        self.comunityname = json_data['community']['name']
        self.communityid = json_data['community']['id']

        return request_info.status_code

    def get_all_user_ids(self):
        """ get all user ids in community

        :return: list containing all user ids
        """

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
            self.userids.append(str(id['id']))

        return self.userids

    def get_aut_token(self):
        """

        :return:
        """
        return self.auth_token

    def get_user_id(self):
        """

        :return:
        """
        return self.userid

    def get_community_id(self):
        """

        :return:
        """
        return self.communityid

    def get_wealth(self, userid):
        """

        :param userid:
        :return:
        """

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
        print(json_data)
        wealth = int(json_data['matchday']['budget'])
        return wealth

    def get_squad(self, userid):
        """

        :param userid:
        :return:
        """

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


if __name__ == '__main__':
    comunio = Comunio()
    print(comunio.login(username='', password=''))
    

