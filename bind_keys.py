import aqt
from . import utilities

def add_shortcuts(shortcuts):
    shortcuts.append(('q', utilities.import_note_types_from_default_directory))

def map_keys_in_previewer(self):
    aqt.qt.QShortcut(aqt.qt.QKeySequence(_("q")), self._previewer, activated=utilities.import_note_types_from_default_directory)

def init():
  # Map key when reviewing cards
  aqt.anki.hooks.addHook("reviewStateShortcuts", add_shortcuts)
  # Map key when previewing cards
  aqt.browser.Browser.onTogglePreview = aqt.anki.hooks.wrap(aqt.browser.Browser.onTogglePreview, map_keys_in_previewer)
