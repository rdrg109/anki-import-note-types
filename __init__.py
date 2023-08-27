import aqt
from . import utilities

menu = aqt.QMenu(aqt.mw.form.menuTools)
menu.setTitle("Import note types")
aqt.mw.form.menuTools.addAction(menu.menuAction())

actions = [
    (aqt.qt.QAction("Import from...", menu), utilities.import_note_types_from_user_selected_directory),
    (aqt.qt.QAction("Import from default directory", menu), utilities.import_note_types_from_default_directory),
]

for action, func in actions:
    aqt.utils.qconnect(action.triggered, func)
    menu.addAction(action)
