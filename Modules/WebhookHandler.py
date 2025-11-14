###############
## LIBRARIES ##
###############
## EXTERNAL ##
import requests
import sys
import json
import time
from os import path

## INTERNAL ##
from .Database import Database
from .Utilities import Utilities
from .Groups import Groups
from .Users import Users
from .Roblox import Roblox

sys.path.append(path.join(path.dirname(__file__), ".."))
from InfoModules.Roles import Roles

###############
## FUNCTIONS ##
###############
## MECAHNICS
def ConstructRoleShowOffEmbedInfo(TotalRoleTimes, GroupHandler, DatabaseHandler):
    OrderedRoleNames = Utilities.SortDictionary(__name__, Dict = TotalRoleTimes)
    OrderedRoleNames.reverse()

    TopRole = OrderedRoleNames[0]
    TotalTimeSpent = TotalRoleTimes[TopRole]

    FormattedTime = Utilities.GetFormattedTimeFromSeconds(__name__, Seconds = TotalTimeSpent)

    Success, Thumbnail = GroupHandler.GetGroupEmblem(Group_id = Roles.GetRoles(__name__)[TopRole])

    if not Success:
        Thumbnail = GroupHandler.GetGroupEmblemByName(GroupName = TopRole)

    EmbedInfo = {
        "EmbedTitle" : "Most Active Role Today",
        "EmbedDescription" : TopRole,
        "FieldTitle" : "Daily Play Time",
        "FieldText" : "`Days: " + str(FormattedTime["Days"]) + " | Hours: " + str(FormattedTime["Hours"]) + " | Minutes: " + str(FormattedTime["Minutes"]) + "`",
        "Thumbnail" : Thumbnail
    }

    return EmbedInfo

def ConstructMultiEmbedInfoForRoleLog(TotalRoleTimes, GroupHandler, DatabaseHandler):
    OrderedRoleNames = Utilities.SortDictionary(__name__, Dict = TotalRoleTimes)
    OrderedRoleNames.reverse()

    EmbedInfos = []

    Rank = 1

    for RoleName in OrderedRoleNames:
        TotalTimeSpent = TotalRoleTimes[RoleName]

        FormattedTime = Utilities.GetFormattedTimeFromSeconds(__name__, Seconds = TotalTimeSpent)

        Success, Thumbnail = GroupHandler.GetGroupEmblem(Group_id = Roles.GetRoles(__name__)[RoleName])

        if not Success:
            Thumbnail = GroupHandler.GetGroupEmblemByName(GroupName = RoleName)

        EmbedInfo = {
            "EmbedTitle" : RoleName,
            "EmbedDescription": "**Rank: #" + str(Rank) + "**",
            "Thumbnail" : Thumbnail
        }

        TopTenPlayers = DatabaseHandler.GetTopTimesInRole(RoleName = RoleName, Number = 10)

        Fields = []

        Field1 = {
            "name" : "Daily Play Time",
            "value" : "`Days: " + str(FormattedTime["Days"]) + " | Hours: " + str(FormattedTime["Hours"]) + " | Minutes: " + str(FormattedTime["Minutes"]) + "`",
        }
        
        Field2 = {
            "name" : "Top 10 players",
        }

        Field2Text = ""

        Index = 1
        for Field in TopTenPlayers:
            UserFormattedTime = Utilities.GetMoreAccurateFormattedTimeFromSeconds(__name__, Seconds = int(Field["TimePlayed"]))
            Field2Text = Field2Text + "`" + str(Index) + ") " + Field["Username"] + " | Hours: " + str(UserFormattedTime["Hours"]) + " | Mins: " + str(UserFormattedTime["Minutes"]) + " | Secs: " + str(UserFormattedTime["Seconds"]) + "`\n"
            Index += 1

        if Field2Text == "":
            Field2Text = "No one was active today from this Role!"

        Field2["value"] = Field2Text

        Fields.append(Field1)
        Fields.append(Field2)

        EmbedInfo["Fields"] = Fields

        EmbedInfos.append(EmbedInfo)
        Rank += 1

    return EmbedInfos
       
def ConstructWebhookEmbedStringForRoleLog(TotalRoleTimes):
    OrderedRoleNames = Utilities.SortDictionary(__name__, Dict = TotalRoleTimes)

    FieldValue = ""
    Index = 1

    for RoleName in OrderedRoleNames:
        TotalTimeSpent = TotalRoleTimes[RoleName]

        FormattedTime = Utilities.GetFormattedTimeFromSeconds(__name__, Seconds = TotalTimeSpent)

        FieldValue = FieldValue + "`" + str(Index) + ") " + RoleName + " | Days: " + str(FormattedTime["Days"]) + " | Hours: " + str(FormattedTime["Hours"]) + " | Minutes: " + str(FormattedTime["Minutes"]) + "`\n"

        Index += 1

    return FieldValue

def GetEmbedInfoForDonation(Json, DatabaseHandler):
    EmbedInfo = {
        "EmbedTitle" : "Donation Log",
        "EmbedDescription" : Json["Username"] + " donated to the group!",
        "FieldTitle" : "Donation Info",
        "FieldText" : "**Most Recent Donation: **" + str(Json["Donated"]) + " R$\n**Total Donated: **" + str(DatabaseHandler.GetPlayerFromDonations(UserId = Json["UserId"])["Donated"]) + " R$",
        "Thumbnail" : Users.GetProfilePictureFromUserId(__name__, Type = "HeadShot", UserId = Json["UserId"])
    }

    return EmbedInfo

class WebhookHandler(object):
    CoreSettings = None
    DatabaseHandler = None
    GroupHandler = None

    def __init__(self, CoreSettings):
        self.CoreSettings = CoreSettings
        self.DatabaseHandler = Database(CoreSettings = self.CoreSettings)
        self.GroupHandler = Groups(self.CoreSettings)

    def GetTotalTimesForEachRole(self, RoleNames):
        RoleTotalTimes = {}

        for RoleName in RoleNames:
            TotalTime = 0
            AllTimesInRole = self.DatabaseHandler.GetAllTimesInRole(RoleName = RoleName)

            for Document in AllTimesInRole:
                TotalTime += int(Document["TimePlayed"])
            
            RoleTotalTimes[RoleName] = TotalTime

        return RoleTotalTimes

    def LogKill(self, Json):
        ## Functions
        ## INIT

        BoolToString = {
            True : "Yes",
            False: "No"
        }

        MurdererProfilePicture = Users.GetProfilePictureFromUserId(__name__, Type = "HeadShot", UserId = Json["Murderer"]["UserId"])
        EmbedTitle = "KILL LOG"
        EmbedDescription = Users.GetUsernameFromUserId(__name__, UserId = Json["Murderer"]["UserId"])
        FieldTitle = "Kill Information"
        FieldText = "**Killed: **" + Json["Target"]["Name"] + "\n**Weapon: **" + Json["Murderer"]["Tool"]["Name"] + "\n**Distance: **" + str(Json["Distance"]) + " studs\n**Headshot: **" + BoolToString[Json["Headshot"]] + "\n**Time: **" + str(Json["Time"]["UTC"]) + " UTC"

        return self.SendEmbedToChannel("Kills", EmbedTitle, EmbedDescription, FieldTitle, FieldText, MurdererProfilePicture)

    def LogArrest(self, Json):
        ## Functions
        ## INIT

        ProfilePicture = Users.GetProfilePictureFromUserId(__name__, Type = "HeadShot", UserId = Json["Arrested"]["UserId"])
        EmbedTitle = "ARREST LOG"
        EmbedDescription = " "
        FieldTitle = "Arrest Information"
        FieldText = "**Arrested: **" + Json["Arrested"]["Username"] + "\n**Arrested by: **" + Json["ArrestedBy"]["Username"] + "\n**Time: **" + Json["Time"] + "\n**Reason: **" + Json["Reason"]

        return self.SendEmbedToChannel("Arrested", EmbedTitle, EmbedDescription, FieldTitle, FieldText, ProfilePicture)

    def LogAdminCommand(self, Json):
        ## Functions
        ## INIT

        ProfilePicture = Users.GetProfilePictureFromUserId(__name__, Type = "HeadShot", UserId = Json["UserId"])
        EmbedTitle = "ADMIN LOG"
        EmbedDescription = Json["Username"]
        FieldTitle = "Command Information"
        FieldText = "`" + Json["Command"] + "`"

        return self.SendEmbedToChannel("AdminLogs", EmbedTitle,  EmbedDescription, FieldTitle, FieldText, ProfilePicture)

    def LogExploiter(self, Json):
        ## Functions
        ## INIT

        ProfilePicture = Users.GetProfilePictureFromUserId(__name__, Type = "HeadShot", UserId = Json["UserId"])
        EmbedTitle = "EXPLOITER LOG"
        EmbedDescription = Json["Username"]
        FieldTitle = "Exploit Information"
        FieldText = "**Warnings: **" + str(Json["Warnings"]) + "\n**Game Link: **" + Roblox.GetPlaceLinkFromPlace_id(__name__, Place_id = Json["Place_id"]) + "\n**Reason: **`" + Json["Reason"] + "`"

        return self.SendEmbedToChannel("ExploiterLogs", EmbedTitle, EmbedDescription, FieldTitle, FieldText, ProfilePicture)

    def LogTopRole(self):
        ## Functions
        ## INIT
        TotalRoleTimes = self.GetTotalTimesForEachRole(Utilities.GetKeysArrays(__name__, Dict = self.CoreSettings["Group"]["Roles"]))
        TopEmbedInfo = ConstructRoleShowOffEmbedInfo(TotalRoleTimes, self.GroupHandler, self.DatabaseHandler)

        return self.SendEmbedToChannel("RoleShowOff", TopEmbedInfo["EmbedTitle"], TopEmbedInfo["EmbedDescription"], TopEmbedInfo["FieldTitle"], TopEmbedInfo["FieldText"], TopEmbedInfo["Thumbnail"])

    def LogRoleTimes(self):
        ## Functions
        ## INIT
        TotalRoleTimes = self.GetTotalTimesForEachRole(Utilities.GetKeysArrays(__name__, Dict = self.CoreSettings["Group"]["Roles"]))
        EmbedInfos = ConstructMultiEmbedInfoForRoleLog(TotalRoleTimes, self.GroupHandler, self.DatabaseHandler)

        self.SendEmbedsToChannel("RoleTimeLogging", EmbedInfos)

        return self.LogTopRole()

    def LogDonation(self, Json):
        ## Functions
        ## INIT
        Response = self.DatabaseHandler.LogDonation(Json = Json)

        if Response == True:
            EmbedInfo = GetEmbedInfoForDonation(Json, self.DatabaseHandler)

            try:
                self.SendEmbedToChannel("Donations", EmbedInfo["EmbedTitle"], EmbedInfo["EmbedDescription"], EmbedInfo["FieldTitle"], EmbedInfo["FieldText"], EmbedInfo["Thumbnail"])
            except:
                print("Donation was not logged!")

    def ResetRoleTimes(self):
        for RoleName in Utilities.GetKeysArrays(__name__, Dict = self.CoreSettings["Group"]["Roles"]):
            self.DatabaseHandler.DeleteAllTimesInRole(RoleName = RoleName)

        return True

    def HandleRequestResult(self, result):
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

    def SendEmbedsToChannel(self, ChannelName, Embeds):
        Data = {
            "username" : self.CoreSettings["Discord"]["Bot"]["Username"],
            "avatar_url" : self.CoreSettings["Discord"]["Bot"]["ProfilePicture"],
            "content" : "",
        }

        TotalEmbeds = []

        DataEmbeds = []

        Count = 0

        for EmbedInfo in Embeds:
            Embed = {
                "title" : EmbedInfo["EmbedTitle"],
                "description" : EmbedInfo["EmbedDescription"],
                "type" : self.CoreSettings["Discord"]["Embed"]["Type"],
                "color" : self.CoreSettings["Discord"]["Embed"]["Colour"],
                "thumbnail" : {
                    "url" : EmbedInfo["Thumbnail"]
                },
                "author" : {
                    "name" : self.CoreSettings["Discord"]["Embed"]["Author"]["Name"],
                    "icon_url" : self.CoreSettings["Discord"]["Embed"]["Author"]["Icon"]
                },
                "fields": [],
                "footer" : {
                    "text" : self.CoreSettings["Discord"]["Embed"]["Footer"]["Text"],
                    "icon_url" : self.CoreSettings["Discord"]["Embed"]["Footer"]["Icon"]
                }
            }


            if "FieldText" in EmbedInfo and "FieldTitle" in EmbedInfo:
                DataToAppend = {
                    "name" : EmbedInfo["FieldTitle"],
                    "value" : EmbedInfo["FieldText"]
                }

                Embed["fields"].append(DataToAppend)

            if "Fields" in EmbedInfo:
                for FieldInfo in EmbedInfo["Fields"]:
                    Embed["fields"].append(FieldInfo)

            DataEmbeds.append(Embed)

            Count += 1

            if Count == 9:
                TotalEmbeds.append(DataEmbeds)

                DataEmbeds = []
                Count = 0

        TotalEmbeds.append(DataEmbeds)

        if self.CoreSettings["Flask"]["Debug"] == True:
            print("Final JSON Data\n\n")
            print(json.dumps(Data, indent = 4, sort_keys = True))

        for TotalEmbed in TotalEmbeds:
            Data["embeds"] = TotalEmbed
            result = requests.post(self.CoreSettings["Discord"]["Webhooks"][ChannelName], json = Data)
            self.HandleRequestResult(result)
            Data["embeds"] = []

        return True

    def SendEmbedToChannel(self, ChannelName, EmbedTitle, EmbedDescription, FieldTitle, Text, Thumbnail):
        Data = {
            "username" : self.CoreSettings["Discord"]["Bot"]["Username"],
            "avatar_url" : self.CoreSettings["Discord"]["Bot"]["ProfilePicture"],
            "content" : "",
            "embeds" : [{
                "title" : EmbedTitle,
                "description" : EmbedDescription,
                "type" : self.CoreSettings["Discord"]["Embed"]["Type"],
                "color" : self.CoreSettings["Discord"]["Embed"]["Colour"],
                "thumbnail" : {
                    "url" : Thumbnail
                },
                "author" : {
                    "name" : self.CoreSettings["Discord"]["Embed"]["Author"]["Name"],
                    "icon_url" : self.CoreSettings["Discord"]["Embed"]["Author"]["Icon"]
                },
                "fields" : [{
                    "name" : FieldTitle,
                    "value" : Text
                }],
                "footer" : {
                    "text" : self.CoreSettings["Discord"]["Embed"]["Footer"]["Text"],
                    "icon_url" : self.CoreSettings["Discord"]["Embed"]["Footer"]["Icon"]
                }
            }]
        }

        result = requests.post(self.CoreSettings["Discord"]["Webhooks"][ChannelName], json = Data)

        self.HandleRequestResult(result)

        return True