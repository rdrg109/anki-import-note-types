import aqt

dict = {}

def reload():
    global dict
    dict = aqt.mw.addonManager.getConfig(__name__)
