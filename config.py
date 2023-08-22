import aqt

dict = {}

def reload():
    global dict
    dict = aqt.mw.addonManager.getConfig(__name__)

def edit():
    aqt.addons.ConfigEditor(aqt.mw, __name__, aqt.mw.addonManager.getConfig(__name__))
