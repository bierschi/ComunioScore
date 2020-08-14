import logging
import requests
import json

from ComunioScore.exceptions import ComunioAccessTokenError


class ComunioRequest:
    """ class ComunioRequest to request basic api data from comunio

    USAGE:
            comrequest = ComunioRequest()
            if comrequest.login(username='', password='')
                comrequest.standings()
    """
    token = None
    community_id = None
    username = None
    password = None

    def __init__(self):
        self.logger = logging.getLogger('ComunioScore')
        self.logger.info('Create class ComunioRequest')

        self.session = requests.Session()
        self.api_url = "https://api.comunio.de/"

        self.standard_header = {
            'Origin': 'http://www.comunio.de',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,en-EN;q=0.9',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
                          'Chromium/60.0.3112.78 Chrome/60.0.3112.78 Safari/537.36',
            'Connection': 'keep-alive',
        }

    def __del__(self):
        """ destructor

        """
        self.close()

    def __set_user_and_community_info(self):
        """ sets user and community specific attributes

        """
        self.standard_header['Authorization'] = 'Bearer ' + ComunioRequest.token
        self.standard_header['Referer'] = 'http://www.comunio.de/dashboard'

        info_request = self.session.get(self.api_url, headers=self.standard_header)

        if info_request.status_code == 401:
            raise ComunioAccessTokenError("Provided access token is invalid!")

        json_data = json.loads(info_request.text)

        self.loggedin_user          = json_data['user']['name']
        self.userid                 = json_data['user']['id']
        self.leader                 = json_data['user']['isLeader']
        self.user_budget            = json_data['user']['budget']
        self.user_teamvalue         = json_data['user']['teamValue']
        self.communityname          = json_data['community']['name']
        ComunioRequest.community_id = json_data['community']['id']

    def close(self):
        """ closes the session object cleanly

        """
        self.session.close()
        self.session.cookies.clear()

    def get_community_name(self):
        """ get community name from logged in user

        :return: community name as string
        """
        return self.communityname

    def get_login_userid(self):
        """ get the userid from the logged in user

        :return: userid
        """
        return self.userid

    def login(self, username, password):
        """ comunio login with username and password

        :param username: username of account
        :param password: password of account
        :return: bool, if login was successful
        """
        self.logger.info("Login to Comunio with username {}".format(username))

        ComunioRequest.username = username
        ComunioRequest.password = password
        login_form = [('username', username), ('password', password)]

        try:
            login_request = self.session.post(self.api_url + 'login', headers=self.standard_header, data=login_form)
        except requests.exceptions.RequestException as e:
            self.logger.error("Comunio login error: {}".format(e))
            return False

        # log error
        if login_request.status_code == 400 or not (login_request.status_code // 100 == 2):
            error_data = login_request.text
            self.logger.error("StatusCode: {} with Description: {}".format(login_request.status_code, error_data))
            return False

        # set auth token data
        json_data = json.loads(login_request.text)
        ComunioRequest.token = str(json_data['access_token'])

        # set mandatory attributes
        self.__set_user_and_community_info()

        return True

    def standings(self):
        """ request standings data from comunio

        :return: standings data as json
        """

        self.standard_header['Authorization'] = 'Bearer ' + ComunioRequest.token
        self.standard_header['Referer'] = 'http://www.comunio.de/standings/total'

        params_standings = (('period', 'season'),)
        standings_request = self.session.get(self.api_url + 'communities/' + ComunioRequest.community_id + '/standings',
                                             headers=self.standard_header, params=params_standings)

        if standings_request.status_code == 401:
            raise ComunioAccessTokenError("Provided access token is invalid!")

        return standings_request.json()

    def squad(self, userid):
        """ get squad data for given userid

        :return: squad data as json
        """

        self.standard_header['Authorization'] = 'Bearer ' + ComunioRequest.token

        squad_request = self.session.get(self.api_url + 'users/' + str(userid) + '/squad', headers=self.standard_header)

        if squad_request.status_code == 401:
            raise ComunioAccessTokenError("Provided access token is invalid!")

        return squad_request.json()

    def squad_latest(self, userid):
        """ get squad latest data for given userid

        :return: squad latest data as json
        """

        self.standard_header['Authorization'] = 'Bearer ' + ComunioRequest.token

        squad_latest_request = self.session.get(self.api_url + 'users/' + str(userid) + '/squad-latest', headers=self.standard_header)

        if squad_latest_request.status_code == 401:
            raise ComunioAccessTokenError("Provided access token is invalid!")

        return squad_latest_request.json()

    def user(self, userid):
        """ get user data for given userid

        :return: user data as json
        """
        self.standard_header['Authorization'] = 'Bearer ' + ComunioRequest.token

        user_request = self.session.get(self.api_url + 'users/' + str(userid), headers=self.standard_header)

        if user_request.status_code == 401:
            raise ComunioAccessTokenError("Provided access token is invalid!")

        return user_request.json()


