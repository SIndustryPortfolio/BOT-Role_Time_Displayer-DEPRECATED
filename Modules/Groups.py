###############
## LIBRARIES ##
###############
import requests
import sys
from os import path
from bs4 import BeautifulSoup

sys.path.append(path.join(path.dirname(__file__), ".."))
from InfoModules.RoleImages import RoleImages

class Groups(object):
    CoreSettings = None

    def __init__(self, CoreSettings):
        self.CoreSettings = CoreSettings

    def GetGroupEmblemByName(self, GroupName):
        return RoleImages.GetRoleImages(__name__)[GroupName]

    def GetGroupEmblem(self, Group_id):
        try:
            response = requests.get(url = "http://api.roblox.com/groups/" + str(Group_id))
        
            jsonResponse = None
            
            try:
                jsonResponse = response.json()
            except:
                print("Json response not available!")
            
            if jsonResponse == None:
                return False, self.CoreSettings["Discord"]["Embed"]["PlaceHolderImage"]
        
            if not "EmblemUrl" in jsonResponse:
                return False, self.CoreSettings["Discord"]["Embed"]["PlaceHolderImage"]

            Asset_id = jsonResponse["EmblemUrl"].replace("http://www.roblox.com/asset/?_id=", "")

            AssetPageUrl = "https://www.roblox.com/library/" + Asset_id

            AssetPageResponse = requests.get(url = AssetPageUrl)

            PageSoup = BeautifulSoup(AssetPageResponse.content, "html.parser")

            GroupImageSpan = PageSoup.find(class_ = "thumbnail-span")

            for childNode in GroupImageSpan.findChildren("img", recursive = False):
                return True, childNode["src"]
            
            return False, self.CoreSettings["Discord"]["Embed"]["PlaceHolderImage"]

        except Exception as E:
            print("Exception: " + str(E))
            return False, self.CoreSettings["Discord"]["Embed"]["PlaceHolderImage"]