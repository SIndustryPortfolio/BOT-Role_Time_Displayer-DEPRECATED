###############
## LIBRARIES ##
###############
## EXTERNAL ##
from flask import Flask, escape, json, request, render_template, jsonify, Response
#from pymongo import MongoClient
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import pymongo
import asyncio
import os
#import schedule
import time

from pytz import timezone, utc

## INTERNAL ##
from InfoModules.Core import Core
from Modules.Roblox import Roblox
from Modules.Utilities import Utilities
from Modules.Database import Database
from Modules.WebhookHandler import WebhookHandler

##########
## CORE ##
##########
CoreSettings = Core().GetSettings()

RootDirectory = os.path.dirname(os.getcwd())
app = Flask(__name__, template_folder = CoreSettings["Flask"]["TemplateFolder"], static_folder = CoreSettings["Flask"]["StaticFolder"])

_DatabaseHandler = Database(CoreSettings = CoreSettings)
_WebhookHandler = WebhookHandler(CoreSettings = CoreSettings)


BoolResponse = {
    True : "Success",
    False : "Error",
    None: "Error"
}

###############
## FUNCTIONS ##
###############
## MECHANICS
def BackgroundSchedulerCheck():
    print("\n\n")
    print("|||| SCHEDULER STILL RUNNING ||||")
    print("<-<--------------------------->->")

    _DatabaseHandler.PruneTryOuts()

def DailyProcedure():
    print("\n\n")
    print("|||| RUNNING DAILY PROCEDURE ||||")
    print("<-<--------------------------->->")

    try:
        _WebhookHandler.LogRoleTimes()
        _DatabaseHandler.FlushDatabase()
    except Exception as E:
        print("Exception: " + str(E))

    return True

def RunWebServer():
    app.run(host = CoreSettings["Flask"]["HostIP"], debug = CoreSettings["Flask"]["Debug"], use_reloader = CoreSettings["Flask"]["UseReloader"], port = os.environ.get("PORT", CoreSettings["Flask"]["DefaultPort"]))

def Authenticate(JSON):
    if JSON["AuthToken"] == CoreSettings["Discord"]["Security"]["AuthToken"]:
        return True
    else:
        return False

def Main():
    print("\n\n")
    print("|||| BOOTING UP ||||")
    print("<-<-------------->->")


    _Scheduler = BackgroundScheduler(daemon = True)
    _Scheduler.add_job(func = DailyProcedure, trigger = "interval", hours = 24)
    _Scheduler.add_job(func = BackgroundSchedulerCheck, trigger = "interval", minutes = 1)
    _Scheduler.start()

    atexit.register(lambda: _Scheduler.shutdown())

    RunWebServer()

## EVENTS ##
# WEB PAGES #
@app.route("/")
def OnRoutePageOpened():
    return BoolResponse[None]

@app.route("/FlushDatabase", methods = ["POST"])
def FlushDatabase():
    print("\n\n")
    print("|||| FLUSHING DATABASE ||||")
    print("<-<--------------------->->")

    return BoolResponse[_DatabaseHandler.FlushDatabase()]

@app.route("/LogTopRole", methods = ["POST"])
def WebLogTopRole():
    return BoolResponse[_WebhookHandler.LogTopRole()]

@app.route("/DailyProcedure", methods = ["POST"])
def WebDailyProcedure():
    return BoolResponse[DailyProcedure()]

@app.route("/LogTryOut", methods = ["POST"])
def WebLogTryOut():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.LogTryOut(Json = Content)]

@app.route("/LogKill", methods = ["POST"])
def WebLogKill():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_WebhookHandler.LogKill(Json = Content)]

@app.route("/LogExploiter", methods = ["POST"])
def WebLogExploiter():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]
    
    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_WebhookHandler.LogExploiter(Json = Content)]

@app.route("/LogArrest", methods = ["POST"])
def WebLogArrest():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_WebhookHandler.LogArrest(Json = Content)]

@app.route("/LogDetainedEvasion", methods = ["POST"])
def WebLogDetainedEvasion():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]
    
    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.LogDetainedEvasion(Json = Content)]

@app.route("/LogAdminCommand", methods = ["POST"])
def WebLogAdminCommand():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]
    
    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_WebhookHandler.LogAdminCommand(Json = Content)]

@app.route("/LogTimeRole", methods = ["POST"])
def WebLogRoleTime():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.LogTimeRequest(Json = Content)]
    
@app.route("/LogNewMember", methods = ["POST"])
def WebLogNewMember():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return _DatabaseHandler.LogNewMemberProcess(Json = Content)

@app.route("/LogWarn", methods = ["POST"])
def WebLogWarn():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]
    
    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.LogWarn(Json = Content)]

@app.route("/LogNewMemberPurchase", methods = ["POST"])
def WebLogNewMemberPurchase():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.LogNewMemberPurchase(Json = Content)]

@app.route("/UnbanUser", methods = ["POST"])
def WebUnbanUser():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]
    
    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.UnlogBan(Json = Content)]

@app.route("/BanUser", methods = ["POST"])
def WebBanUser():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.LogBan(Json = Content)]

@app.route("/FlushDonations", methods = ["POST"])
def WebFlushDonations():
    return BoolResponse[_DatabaseHandler.DeleteAllDonations()]

@app.route("/LogDonation", methods = ["POST"])
def WebLogDonation():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]
    
    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_WebhookHandler.LogDonation(Json = Content)]

@app.route("/GetWarns", methods = ["POST", "GET"])
def WebGetWarns():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    Response = _DatabaseHandler.GetWarns(Json = Content)

    if Response == None:
        return BoolResponse[None]
    else:
        return jsonify(Response)

@app.route("/HasNewMemberPurchased", methods = ["POST", "GET"])
def WebHasNewMemberPurchased():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.HasNewMemberPurchased(Json = Content)]

@app.route("/GetTotalDonated", methods = ["POST", "GET"])
def WebGetTotalDonated():
    return str(_DatabaseHandler.GetTotalDonated())

@app.route("/GetNewMemberPurchased", methods = ["POST", "GET"])
def WebGetNewMemberPurchased():
    if not request.json:
        print("Request is not JSON")
        return BoolResponse[None]
    
    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    Response = _DatabaseHandler.GetNewMemberPurchased(Json = Content)

    if Response == None:
        return BoolResponse[None]
    else:
        return jsonify(Response)

@app.route("/GetBanInfo", methods = ["POST", "GET"])
def WebGetBanInfo():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    Response = _DatabaseHandler.GetBanInfo(Json = Content)

    if Response == None:
        return BoolResponse[True]
    else:
        return jsonify(Response)

@app.route("/DeleteDetainedEvasion", methods = ["POST"])
def WebDeleteDetainedEvasion():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    return BoolResponse[_DatabaseHandler.DeleteDetainedEvasion(Json = Content)]

@app.route("/GetDetainedEvasion", methods = ["POST", "GET"])
def WebGetDetainedEvasion():
    if not request.is_json:
        print("Request is not JSON")
        return BoolResponse[None]

    Content = request.json

    if not Authenticate(Content):
        return BoolResponse[None]

    Response = _DatabaseHandler.GetDetainedEvasion(Json = Content)

    if Response == None:
        return BoolResponse[None]
    else:
        return jsonify(Response)

@app.route("/GetTick", methods = ["POST", "GET"])
def WebGetTick():
    return str(Utilities.Tick(__name__))

@app.route("/GetTryOuts", methods = ["POST", "GET"])
def WebGetTryOuts():
    return jsonify(_DatabaseHandler.GetTryOuts())

@app.route("/GetBans", methods = ["POST", "GET"])
def WebGetBans():
    return jsonify(result = _DatabaseHandler.GetBans())

## INIT ##
#schedule.every().day.at("00:00").do(DailyProcedure)

if __name__ == "__main__":
    Main()
