import aqt
from . import templates

def _edit_config():
    aqt.addons.ConfigEditor(aqt.mw, __name__, aqt.mw.addonManager.getConfig(__name__))

def init():
    # menu items
    menu = aqt.QMenu(aqt.mw.form.menuTools)
    menu.setTitle("Import / Export templates")
    aqt.mw.form.menuTools.addAction(menu.menuAction())

    actions = [
        (aqt.qt.QAction("Export to ...", menu), templates.export_tmpls),
        (aqt.qt.QAction("Import from ...", menu), templates.import_note_types_from_user_selected_directory),
        (aqt.qt.QAction("Import from default directory", menu), templates.import_note_types_from_default_directory),
        (aqt.qt.QAction("Configure", menu), _edit_config)
    ]

    for action, func in actions:
        aqt.utils.qconnect(action.triggered, func)
        menu.addAction(action)

    # editor setup for _edit_config
    aqt.mw.mgr = aqt.mw.addonManager

def get_dir():
    folder = aqt.QFileDialog.getExistingDirectory(aqt.mw, "Select a Directory")
    if len(folder) != 0:
        return folder
    return None


