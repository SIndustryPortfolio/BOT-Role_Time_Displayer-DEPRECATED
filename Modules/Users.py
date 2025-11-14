###############
## LIBRARIES ##
###############
## EXTERNAL ##
import requests

class Users(object):
    def GetProfilePictureFromUserId(self, UserId, Type):
        TypeToLink = {
            "HeadShot" : "https://www.roblox.com/headshot-thumbnail/image?UserId={}&w_idth=420&height=420&format=png",
            "Bust" : "https://www.roblox.com/bust-thumbnail/image?UserId={}&w_idth=420&height=420&format=png",
        }

        return str(TypeToLink[Type]).format(str(UserId))

    def GetUsernameFromUserId(self, UserId):
        response = requests.get(url = "https://api.roblox.com/users/" + str(UserId))

        jsonResponse = None

        try:
            jsonResponse = response.json()
        except:
            print("Json response is not available!")

        if "Username" in jsonResponse:
            return jsonResponse["Username"]
        else:
            return "Unknown Username | Test Account"