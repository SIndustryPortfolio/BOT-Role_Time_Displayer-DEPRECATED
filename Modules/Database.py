###############
## LIBRARIES ##
###############
## EXTERNAL ##
from pymongo import MongoClient
from datetime import date

## INTERNAL ##
from .Utilities import Utilities

class Database(object):
    ## CORE
    Cluster = None
    RoleDatabase = None
    MiscDatabase = None

    ## Functions
    ## MECHANICS

    def GetMiscCollection(self, MiscCollectionName):
        if MiscCollectionName in self.MiscDatabase.list_collection_names():
            return self.MiscDatabase[MiscCollectionName]
        else:
            return None

    def GetRoleCollection(self, RoleName):
        if RoleName in self.RoleDatabase.list_collection_names():
            return self.RoleDatabase[RoleName]
        else:
            return None

    def GetTopTimesInRole(self, RoleName, Number):
        RoleCollection = self.GetRoleCollection(RoleName)

        if RoleCollection == None:
            return None

        AllFields = RoleCollection.find().sort("TimePlayed", -1)
    
        Index = 1
        NewList = []

        for Field in AllFields:
            NewList.append(Field)

            if Index >= Number:
                break
            else:
                Index += 1
        
        return NewList

    ## DIRECT
    def __init__(self, CoreSettings):
        self.Cluster = MongoClient("mongodb+srv://" + CoreSettings["MongoDB"]["Client"]["Username"] + ":" + CoreSettings["MongoDB"]["Client"]["Password"] + ".mongodb.net/" + CoreSettings["MongoDB"]["RoleDatabaseName"] + "?retryWrites=true&w=majority")
        self.RoleDatabase = self.Cluster[CoreSettings["MongoDB"]["RoleDatabaseName"]]
        self.MiscDatabase = self.Cluster[CoreSettings["MongoDB"]["MiscDatabaseName"]]
        self.CoreSettings = CoreSettings

    def GetBans(self):
        ## Functions
        ## INIT
        Bans = []

        BansCollection = self.GetMiscCollection("Bans")

        for FieldInfo in BansCollection.find({}):
            Info = {
                "_id": FieldInfo["_id"],
                "Banner_id": FieldInfo["Banner_id"],
                "Reason": FieldInfo["Reason"]
            }

            Bans.append(Info)

        return Bans

    def GetBanInfo(self, Json):
        ## Functions
        ## INIT
        BansCollection = self.GetMiscCollection("Bans")

        return BansCollection.find_one({"_id" : str(Json["UserId"])})

    def UnlogBan(self, Json):
        ## Functions
        ## INIT

        BansCollection = self.GetMiscCollection("Bans")
        BansCollection.delete_one({"_id" : str(Json["Banned"]["UserId"])})

        return True

    def UpdateWarns(self, Json):
        ## Functions
        ## INIT

        WarnsSettings = self.CoreSettings["Warns"]

        TimeNow = Utilities.Tick(__name__)

        WarnsCollection = self.GetMiscCollection("Warns")

        FoundOldDocument = WarnsCollection.find_one({"_Id": str(Json["UserId"])})

        if FoundOldDocument == None:
            return None

        LogsToRemove = []

        for x in range(0, len(FoundOldDocument["Warns"])):
            Log = FoundOldDocument["Warns"][x]

            DifferenceInTimeInSeconds = TimeNow - Log["Time"]

            NumberOfDays = DifferenceInTimeInSeconds / (24 * 3600)

            if NumberOfDays >= WarnsSettings["LogTime"]:
                LogsToRemove.append(Log) 

        for x in range(0, len(LogsToRemove)):
            Log = LogsToRemove[x]

            Index = LogsToRemove.index(Log)

            if Index != None:
                FoundOldDocument["Warns"].pop(Index)
            
        return True

    def GetWarns(self, Json):
        ## Functions
        ## INIT
        self.UpdateWarns(Json = Json)

        WarnsCollection = self.GetMiscCollection("Warns")
        
        FoundOldDocument = WarnsCollection.find_one({"_id": str(Json["UserId"])})

        if FoundOldDocument:
            return FoundOldDocument
        else:
            return None

    def LogWarn(self, Json):
        ## Functions
        ## INIT

        TimeOfWarn = Utilities.Tick(__name__)

        WarnsCollection = self.GetMiscCollection("Warns")
        
        FoundOldDocument = WarnsCollection.find_one({"_id": str(Json["UserId"])})

        DocumentToEdit = FoundOldDocument

        if FoundOldDocument == None:
            DocumentToEdit = {"_id": str(Json["UserId"]), "Warns": []}
        
        DocumentToEdit["Warns"].append({
            "WarnedBy" : Json["WarnerId"],
            "Reason": Json["Reason"],
            "Time": str(TimeOfWarn),
            "Date" : str(date.today())
        })

        if FoundOldDocument == None:
            WarnsCollection.insert_one(DocumentToEdit)
        else:
            WarnsCollection.replace_one({"_id": Json["UserId"]}, DocumentToEdit)

        self.UpdateWarns(Json = Json)

        return True

    def LogDetainedEvasion(self, Json):
        ## Functions
        ## INIT

        DetainedEvasionsCollection = self.GetMiscCollection("DetainedEvasions")

        FoundOldDocument = DetainedEvasionsCollection.find_one({"_id": str(Json["Detained"]["UserId"])})

        if FoundOldDocument == None:
            DetainedEvasionsCollection.insert_one({"_id": str(Json["Detained"]["UserId"]), "Detainer_id": str(Json["Detainer"]["UserId"])})

        return True

    def DeleteDetainedEvasion(self, Json):
        ## Functions
        ## INIT

        DetainedEvasionCollection = self.GetMiscCollection("DetainedEvasions")

        FoundDocument = DetainedEvasionCollection.find_one({"_id": str(Json["UserId"])})

        if FoundDocument != None:
            DetainedEvasionCollection.delete_one({"_id": str(Json["UserId"])})

        return True

    def GetDetainedEvasion(self, Json):
        ## Functions
        ## INIT

        DetainedEvasionCollection = self.GetMiscCollection("DetainedEvasions")

        FoundDocument = DetainedEvasionCollection.find_one({"_id": str(Json["UserId"])})

        if FoundDocument != None:
            return FoundDocument
        else:
            return None

    def LogBan(self, Json):
        ## Functions
        ## INIT

        BansCollection = self.GetMiscCollection("Bans")
        
        FoundOldDocument = BansCollection.find_one({"_id" : str(Json["Banned"]["UserId"])})

        if FoundOldDocument == None:
            BansCollection.insert_one({"_id" : str(Json["Banned"]["UserId"]), "Banner_id" : str(Json["Banner"]["UserId"]), "Reason" : Json["Reason"]})

        return True

    def IsNewMember(self, Json):
        ## Functions
        ## INIT

        NewMembersCollection = self.GetMiscCollection("NewMembers")

        FoundOldDocument = NewMembersCollection.find_one({"_id": str(Json["UserId"])})

        if FoundOldDocument != None:
            return True
        
        return None

    def LogNewMemberProcess(self, Json):
        ## Functions
        ## INIT

        NewMembersCollection = self.GetMiscCollection("NewMembers")

        if self.HasNewMemberPurchased(Json):
            return " "

        if self.IsNewMember(Json) == None:
            NewMembersCollection.insert_one({"_id" : str(Json["UserId"]), "Time" : str(Json["Time"])})

        return NewMembersCollection.find_one({"_id" : str(Json["UserId"])})["Time"]


    def GetNewMemberPurchased(self, Json):
        ## Functions
        ## INIT

        NewMemberPurchasesCollection = self.GetMiscCollection("NewMemberPurchases")

        FoundOldDocument = NewMemberPurchasesCollection.find_one({"_id" : str(Json["UserId"])})

        if FoundOldDocument:
            return FoundOldDocument

    def HasNewMemberPurchased(self, Json):
        ## Functions
        ## INIT

        NewMemberPurchasesCollection = self.GetMiscCollection("NewMemberPurchases")

        FoundOldDocument = NewMemberPurchasesCollection.find_one({"_id": str(Json["UserId"])})

        if FoundOldDocument != None:
            return True
        else:
            return False

    def LogNewMemberPurchase(self, Json):
        ## Functions
        # INIT
        NewMemberPurchasesCollection = self.GetMiscCollection("NewMemberPurchases")
        NewMembersCollection = self.GetMiscCollection("NewMembers")

        if NewMembersCollection.find_one({"_id" : str(Json["UserId"])}):
            NewMembersCollection.delete_one({"_id": str(Json["UserId"])})

        if self.HasNewMemberPurchased(Json) == False:
            NewMemberPurchasesCollection.insert_one({"_id": str(Json["UserId"]), "Time": str(Utilities.Tick(__name__))})

        return True

    def GetTotalDonated(self):
        ## Functions
        ## INIT

        DonationsCollection = self.GetMiscCollection("Donations")
        AllDonationDocuments = DonationsCollection.find({})

        TotalDonated = 0

        for Document in AllDonationDocuments:
            TotalDonated += Document["Donated"]

        return TotalDonated

    def GetTryOuts(self):
        ## CORE
        TryOuts = []
        
        ## Functions
        ## INIT

        TryOutsCollection = self.GetMiscCollection("TryOuts")
        
        for FieldInfo in TryOutsCollection.find({}):
            Info = {
                "Role" : FieldInfo["Role"],
                "Time" : FieldInfo["Time"],
                "ServerNumber" : FieldInfo["ServerNumber"]
            }

            TryOuts.append(Info)

        return TryOuts

    def PruneTryOuts(self):
        ## Functions
        ## INIT
        TimeNow = Utilities.Tick(__name__)

        TryOutsCollection = self.GetMiscCollection("TryOuts")

        IdsToPrune = []

        for FieldInfo in TryOutsCollection.find({}):
            # print("Scheduled Time: " + str(FieldInfo["Time"]))
            # print("Time Now: " + str(TimeNow))
            if FieldInfo["Time"] < TimeNow:
                IdsToPrune.append(FieldInfo["_id"])

        print("Pruning Ids")
        print(IdsToPrune)

        for Id in IdsToPrune:
            TryOutsCollection.delete_one({"_id" : Id})

        return True

    def LogTryOut(self, Json):
        ## Functions
        ## INIT

        TryOutsCollection = self.GetMiscCollection("TryOuts")
        TryOutsCollection.insert_one({"Role" : Json["Role"], "Time" : Json["Time"], "ServerNumber" : Json["ServerNumber"]})

        return True

    def LogDonation(self, Json):
        ## Functions
        ## INIT

        DonationsCollection = self.GetMiscCollection("Donations")

        FoundOldDocument = DonationsCollection.find_one({"_id" : str(Json["UserId"])})

        if FoundOldDocument != None:
            DonationsCollection.update_one({"_id" : str(Json["UserId"])}, {"$set" : {"Donated" : int(FoundOldDocument["Donated"]) + int(Json["Donated"])}})
        else:
            DonationsCollection.insert_one({"_id" : str(Json["UserId"]), "Username" : Json["Username"], "Donated" : Json["Donated"]})

        return True

    def LogTimeRequest(self, Json):
        ## Functions
        ## INIT

        for key in Json:
            print(str(key) + " : " + str(Json[key]))

        if not "Role" in Json:
            print("Role isn't in JSON")
            return None

        RoleCollection = self.GetRoleCollection(Json["Role"])

        if RoleCollection == None:
            print("Collection doesn't exist")
            return None

        FoundOldDocument = RoleCollection.find_one({"_id" : str(Json["UserId"])})

        if FoundOldDocument == None:
            FoundOldDocument = RoleCollection.find_one({"Username" : str(Json["Username"])})

        if FoundOldDocument != None:
            RoleCollection.update_one({"_id" : str(Json["UserId"])}, {"$set" : {"TimePlayed" : int(FoundOldDocument["TimePlayed"]) + int(Json["TimePlayed"])}})
        else:
            RoleCollection.insert_one({"_id" : str(Json["UserId"]), "Username" : Json["Username"], "TimePlayed" : Json["TimePlayed"]})

        return True
    
    def GetPlayerFromDonations(self, UserId):
        return self.GetMiscCollection("Donations").find_one({"_id" : str(UserId)})

    def DeleteAllDonations(self):
        ## Functions
        ## INIT
        DonationsCollection = self.GetMiscCollection("Donations")

        DonationsCollection.delete_many({})

        return True

    def DeleteAllTimesInRole(self, RoleName):
        ## Functions
        ## INIT
        RoleCollection = self.GetRoleCollection(RoleName)

        if RoleCollection == None:
            print(RoleName + " does not exist!")

        return RoleCollection.delete_many({})

    def FlushDatabase(self):
        ## Functions
        ## INIT
        for RoleName in self.CoreSettings["Group"]["Roles"]:
            self.DeleteAllTimesInRole(RoleName)

        TryOutsCollection = self.GetMiscCollection("TryOuts")
        TryOutsCollection.delete_many({})

        return True

    def GetAllTimesInRole(self, RoleName):
        ## Functions
        ## INIT
        RoleCollection = self.GetRoleCollection(RoleName)

        return RoleCollection.find({})