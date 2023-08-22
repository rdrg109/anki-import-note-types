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

def export_note_types():
    root = utilities.prompt_for_directory()
    if not root:
        return
    config.reload()

    count_notetype = 0
    count_template = 0
    for nt in aqt.mw.col.models.all():
        try:
            notetype_name = nt.get(key_name_anki_model_template_name)
        except KeyError:
            gui.show_error("The notetype has no name!!")
            continue
        notetype_name_stripped = notetype_name.strip()
        if notetype_name_stripped != notetype_name:
            gui.show_error("⚠ Leading and/or trailing spaces detected in notetype name \"{}\". They have be removed "
                           "on export. Before reimporting the template, you will need to remove them in the notetype "
                           "name.".format(notetype_name))
        notetype_path = os.path.join(root, notetype_name_stripped)
        os.makedirs(notetype_path, exist_ok=True)
        # Create text file containing all fields
        with open(os.path.join(notetype_path, 'fields.json'), "w", encoding="utf-8") as f:
            # As of v⁨2.1.65, the dictionary of each field has an "ord"
            # key which is equal to the corresponding index in the
            # list of fields. When a field doesn't have this key, Anki
            # shows an error when editing the fields through the
            # interface.  Although this number can be automatically
            # generated and users might wonder what is its purpose in
            # fields.json, we still store it in fields.json, to avoid
            # doing magickery for ensuring that this value exists. The
            # user should konw that this number shouldn't be edited by
            # hand.
            f.write(json.dumps(nt[key_name_anki_model_fields], indent=2))
        # Create CSS file associated with the note type
        if key_name_anki_model_css in nt:
            with open(os.path.join(notetype_path, config_css_name), "w", encoding="utf-8") as f:
                f.write(nt[key_name_anki_model_css])
        # Create a directory for each card type. Each directory
        # contains a HTML file for the Front Template and the Back
        # Template.
        for tmpl in nt.get(key_name_anki_model_templates, []):
            try:
                tmpl_name = tmpl.get(key_name_anki_model_template_name)
            except KeyError:
                gui.show_error("A template in notetype \"{}\" has no name!!".format(notetype_name))
                continue
            # file_path_dir stores the name of the directory for a card type
            file_path_dir = os.path.join(notetype_path, tmpl_name) + '/'
            if not os.path.isdir(file_path_dir):
                os.makedirs(file_path_dir)
            file_path_front = os.path.join(file_path_dir, 'front.html')
            file_path_back = os.path.join(file_path_dir, 'back.html')
            if key_name_anki_model_template_front in tmpl:
                with open(file_path_front, "w", encoding="utf-8") as f:
                    f.write(tmpl[key_name_anki_model_template_front])
            if key_name_anki_model_template_front in tmpl:
                with open(file_path_back, "w", encoding="utf-8") as f:
                    f.write(tmpl[key_name_anki_model_template_back])
            count_template += 1
        count_notetype += 1
    gui.notify("exported (Template: {} from NoteType:{})".format(count_template, count_notetype)
)
