###############
## LIBRARIES ##
###############
import requests
import sys
from os import path
from bs4 import BeautifulSoup

sys.path.append(path.join(path.dirname(__file__), ".."))
from InfoModules.Roles import Roles

class Roblox(object):
    def GetPlaceLinkFromPlaceId(self, PlaceId):
        return "https://www.roblox.com/games/" + str(PlaceId)