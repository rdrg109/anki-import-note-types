from PyQt5 import QtCore
from aqt import mw as window, utils, qt, addons
import aqt
from . import templates
import os


def _edit_config():
    addons.ConfigEditor(window, __name__, window.addonManager.getConfig(__name__))

def init():
    # menu items
    menu = aqt.QMenu(window.form.menuTools)
    menu.setTitle("Import / Export templates")
    window.form.menuTools.addAction(menu.menuAction())

    actions = [
        (qt.QAction("Export to ...", menu), templates.export_tmpls),
        (qt.QAction("Import from ...", menu), templates.import_note_types_from_user_selected_directory),
        (qt.QAction("Import from default directory", menu), templates.import_note_types_from_default_directory),
        (qt.QAction("Configure", menu), _edit_config)
    ]

    for action, func in actions:
        utils.qconnect(action.triggered, func)
        menu.addAction(action)

    # editor setup for _edit_config
    window.mgr = window.addonManager

def get_dir():
    folder = aqt.QFileDialog.getExistingDirectory(window, "Select a Directory")
    if len(folder) != 0:
        return folder
    return None


