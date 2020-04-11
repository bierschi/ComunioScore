__title__ = "ComunioScore"
__version_info__ = ('1', '0', '2')
__version__ = ".".join(__version_info__)
__author__ = "Christian Bierschneider"
__email__ = "christian.bierschneider@web.de"
__license__ = "MIT"

import os
from ComunioScore.dbhandler import DBHandler
from ComunioScore.comunio import Comunio
from ComunioScore.dbagent import DBAgent
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
