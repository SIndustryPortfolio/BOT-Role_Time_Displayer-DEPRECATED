###############
## LIBRARIES ##
###############
## EXTERNAL ##
import math
import time

class Utilities(object):
    def Tick(self):
        return time.time()

    def DoesDictionaryHaveKeys(self, Dict, Keys):
        for x in range(1, len(Keys)):
            if not Keys[x] in Dict:
                return False
            
        return True
    
    def GetKeysArrays(self, Dict):
        Keys = []

        for Key in Dict:
            Keys.append(Key)

        return Keys

    def GetMoreAccurateFormattedTimeFromSeconds(self, Seconds):
        FormattedDict = {}

        FormattedDict["Hours"] = math.floor(Seconds / 3600)
        Seconds -= (FormattedDict["Hours"] * 3600)
        FormattedDict["Minutes"] = math.floor(Seconds / 60)
        Seconds -= (FormattedDict["Minutes"] * 60)
        FormattedDict["Seconds"] = Seconds

        return FormattedDict

    def GetFormattedTimeFromSeconds(self, Seconds):
        FormattedDict = {}

        FormattedDict["Days"] = math.floor(Seconds / (24 * 3600))
        Seconds -= (FormattedDict["Days"] * 24 * 3600)
        FormattedDict["Hours"] = math.floor(Seconds / 3600)
        Seconds -= (FormattedDict["Hours"] * 3600)
        FormattedDict["Minutes"] = math.floor(Seconds / 60)

        return FormattedDict


    def SortDictionary(self, Dict):
        OrderedKeys = Utilities.GetKeysArrays(__name__, Dict = Dict)
        Sorted = False

        while not Sorted:
            Pass = True

            for x in range(0, len(OrderedKeys) - 1):
                if Dict[OrderedKeys[x]] > Dict[OrderedKeys[x + 1]]:
                    Item1ToSwap = OrderedKeys[x]
                    OrderedKeys.pop(x)
                    OrderedKeys.insert(x + 1, Item1ToSwap)

                    Pass = False

            if Pass:
                Sorted = True

        return OrderedKeys
