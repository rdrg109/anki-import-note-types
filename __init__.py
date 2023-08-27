import aqt
from . import utilities, config, bind_keys

menu = aqt.QMenu(aqt.mw.form.menuTools)
menu.setTitle("Import / Export templates")
aqt.mw.form.menuTools.addAction(menu.menuAction())

actions = [
    (aqt.qt.QAction("Export to...", menu), utilities.export_note_types),
    (aqt.qt.QAction("Import from...", menu), utilities.import_note_types_from_user_selected_directory),
    (aqt.qt.QAction("Import from default directory", menu), utilities.import_note_types_from_default_directory),
    (aqt.qt.QAction("Edit config", menu), config.edit)
]

for action, func in actions:
    aqt.utils.qconnect(action.triggered, func)
    menu.addAction(action)

# We do this in order to pass "mw" to "ConfigEditor" as parent widget
aqt.mw.mgr = aqt.mw.addonManager
bind_keys.init()
