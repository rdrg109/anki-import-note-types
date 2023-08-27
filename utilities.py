import aqt
import os
from . import config, models

class LogText():
    def __init__(self, text=None):
        if text:
            self.text = text
        else:
            self.text = []
    def add_line(self, string):
        self.text.append(string)
    def get(self):
        return '\n'.join(self.text)
    def show(self):
        aqt.mw.utils.showText(self.get())

def prompt_for_directory():
    folder = aqt.QFileDialog.getExistingDirectory(aqt.mw, "Select a Directory")
    # If the user didn't select a directory, then the length is zero.
    #
    # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QFileDialog.html#PySide2.QtWidgets.PySide2.QtWidgets.QFileDialog.getExistingDirectoryUrl
    # , if the user selects an empty directory, the function
    if len(folder) != 0:
        return folder

def import_note_types_from_default_directory():
    config.reload()
    default_directory = config.dict['default-directory']
    if not os.path.isdir(default_directory):
        LogText(f"The provided path is not an existing directory: {default_directory}").show()
        return
    import_note_types_from_directory(default_directory)

def import_note_types_from_user_selected_directory():
    selected_directory = prompt_for_directory()
    if selected_directory:
        import_note_types_from_directory(selected_directory)

def import_note_types_from_directory(root):
    log_text = LogText()
    count_created_model = 0
    file_path_dir_note_types = [os.path.join(root, item)
                                for item in os.listdir(root)
                                if os.path.isdir(os.path.join(root, item))]

    for file_path_dir_note_type in file_path_dir_note_types:
        note_type_name = os.path.basename(file_path_dir_note_type)
        # Collect fields
        file_path_fields = os.path.join(file_path_dir_note_type, 'fields.txt')
        fields = []
        if os.path.exists(file_path_fields):
            with open(file_path_fields, 'r') as f:
                for line in f:
                    if line.strip() == "" or line[0] == "#":
                        continue
                    fields.append(line.strip())
        # Collect CSS
        file_path_css = os.path.join(file_path_dir_note_type, 'style.css')
        css = None
        if os.path.exists(file_path_css):
            with open(file_path_css, "r", encoding="utf-8") as f:
                css = f.read()
        # Collect all card types
        #
        # Iterate through all directories that exist inside the
        # directory of a note type. Each directory correspond to a
        # card type and generally contain two files: front.html and
        # back.html.
        file_path_dir_card_types = [os.path.join(file_path_dir_note_type, x)
                                   for x in os.listdir(os.path.join(file_path_dir_note_type))
                                   if os.path.isdir(os.path.join(file_path_dir_note_type, x))]
        card_types = []
        for file_path_dir_card_type in file_path_dir_card_types:
            card_type = {
                'name': os.path.basename(file_path_dir_card_type)
            }
            file_path_front = os.path.join(file_path_dir_card_type, 'front.html')
            file_path_back = os.path.join(file_path_dir_card_type, 'back.html')
            if os.path.exists(file_path_front):
                with open(file_path_front, "r", encoding="utf-8") as f:
                    card_type['front'] = f.read()
            if os.path.exists(file_path_back):
                with open(file_path_back, "r", encoding="utf-8") as f:
                    card_type['back'] = f.read()
            card_types.append(card_type)
        model = aqt.mw.col.models.by_name(note_type_name)
        # If the note type exists, update it.
        if model:
            models.update_model(
                model = model,
                css = css,
                card_types = card_types,
                fields = fields,
                log_text = log_text)
        # If the model doesn't exist, create it
        else:
            models.create_model(
                name = note_type_name,
                fields = fields,
                card_types = card_types,
                css = css)
            log_text.add_line(f"Note type was created: {note_type_name}")
            count_created_model = count_created_model + 1
    log_text.add_line(f"Number of created models: {count_created_model}")
    aqt.utils.showText(log_text.get())
