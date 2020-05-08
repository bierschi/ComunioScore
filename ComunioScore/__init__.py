__title__ = "ComunioScore"
__version_info__ = ('1', '0', '9')
__version__ = ".".join(__version_info__)
__author__ = "Christian Bierschneider"
__email__ = "christian.bierschneider@web.de"
__license__ = "MIT"

import os
from ComunioScore.dbhandler import DBHandler
from ComunioScore.comunio import Comunio
from ComunioScore.api import APIHandler
from ComunioScore.comuniodb import ComunioDB
from ComunioScore.sofascoredb import SofascoreDB
from ComunioScore.scheduler import Scheduler
from ComunioScore.pointcalculator import PointCalculator

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

