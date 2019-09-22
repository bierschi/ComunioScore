import configparser
from ComunioScore import ROOT_DIR
from ComunioScore.comunio import Comunio

config = configparser.ConfigParser()
config.read(ROOT_DIR + '/config/cfg.ini')

def main():

    username = config.get('comunio', 'username')
    password = config.get('comunio', 'password')

    comunio = Comunio()
    comunio.login(username=username, password=password)
    squad = comunio.get_squad(comunio.get_user_id())
    print(comunio.get_all_user_ids())
    for player in squad:
        print(player['name'])

if __name__ == '__main__':
    main()
