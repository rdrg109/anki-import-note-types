import aqt

dict_config = {}

def reload_config():
    global dict_config
    dict_config = aqt.mw.addonManager.getConfig(__name__)
