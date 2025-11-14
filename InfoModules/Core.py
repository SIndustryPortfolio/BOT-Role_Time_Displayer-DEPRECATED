###############
## LIBRARIES ##
###############
## EXTERNAL ##
from os import path
import os
import sys

## INTERNAL ##
from .Roles import Roles

sys.path.append(path.join(path.dirname(__file__), ".."))
from Modules.Utilities import Utilities

## CORE
Settings = {

    "Scheduler" : {
        "daemon" : True
    },


    "Warns": {
        "LogTime" : os.environ.get("WarnsLogTime") # Days
    },

    "MongoDB" : {
        "RoleDatabaseName" : "Roles",
        "MiscDatabaseName" : "Misc",
        #"CollectionName" : "Roles",

        "Client" : {
            "Username" : os.environ.get("DBUsername"),
            "Password" : os.environ.get("DBPassword")
        }
    },
    
    "Flask" : {
        "TemplateFolder" : "Templates",
        "StaticFolder" : "Static",
        "HostIP" : "0.0.0.0",
        "Debug" : True,
        "DefaultPort" : 5000,
        "UseReloader" : False
    },

    "Group" : {
        "Roles" : Roles.GetRoles(__name__)
    },


    "Discord" : {
        "Security" : 
        {
           "AuthToken" : os.environ.get("AuthToken") 
        },

        "Webhooks" : {
            "RoleTimeLogging" : os.environ.get("RoleTimeLoggingProduction"),
            "Arrested" : os.environ.get("Arrested"),
            "AdminLogs" : os.environ.get("AdminLogs"),
            "ExploiterLogs" : os.environ.get("ExploiterLogs"),
            "RoleShowOff" : os.environ.get("RoleShowOff"),
            "Kills" : os.environ.get("Kills"),
            "Donations" : os.environ.get("Donations")
        },
        "Bot" : {
            "Username" : "ADMIN",
            "ProfilePicture" : ""
        },
        "Embed" : {
            "Title" : "",
            "Description" : "",
            "Type" : "rich",
            "Colour" : int("0xfc0303",  0),
            "Author" : {
                "Name" : os.environ.get("BotName"),
                "Icon" : ""
            },
            "Footer" : {
                "Text" : "Created by " + os.environ.get("OwnerDiscord"),
                "Icon" : ""
            },
            "PlaceHolderImage": "",
        }
    }
}

## Functions
class Core(object):
    def GetSettings(self):
        return Settings
