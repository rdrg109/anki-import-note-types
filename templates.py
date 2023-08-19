import os
import json
import aqt
from . import gui, utils

# key names used by Anki
key_name_anki_model_css = "css"
key_name_anki_model_fields = "flds"
key_name_anki_model_templates = "tmpls"
key_name_anki_model_template_name = "name"
key_name_anki_model_template_front = "qfmt"
key_name_anki_model_template_back = "afmt"

# config
config_delimiter: str = "```\n"
config_css_name: str = "style.css"
config_tmpl_ext: str = ""

def update_model(model, fields, card_types, css):
    model[key_name_anki_model_css] = css
    current_templates = model['tmpls']
    for card_type in card_types:
        index = next((i for i, item in enumerate(current_templates) if item['name'] == card_type['name']), None)
        # In this conditional, we shouldn't write "if index:", because
        # when the index is 0, it will evaluate to False, when index
        # is 0, we want to evaluate to True.
        if index != None:
            current_templates[index]['qfmt'] = card_type['front']
            current_templates[index]['afmt'] = card_type['back']
        else:
            template = aqt.mw.col.models.new_template(card_type['name'])
            template['qfmt'] = card_type['front']
            template['afmt'] = card_type['back']
            aqt.mw.col.models.add_template(model, template)
    aqt.mw.col.models.save(model)

def create_model(name, fields, card_types, css):
    # create_model('My model', ['field 1', 'field 2', 'field 3'], [
    #     {
    #         'name': 'My card type 1',
    #         'front': '{{foo1}}',
    #         'back': '{{foo32}}'
    #     },
    #     {
    #         'name': 'My card type 2',
    #         'front': '{{foo2}}',
    #         'back': '{{foo1}}'
    #     },
    #     {
    #         'name': 'My card type 3',
    #         'front': '{{foo3}}',
    #         'back': '{{foo1}}'
    #     }])
    # Create new model
    new_model = aqt.mw.col.models.new(name)
    # Add CSS
    if css:
        new_model['css'] = css
    # Add fields
    for i in fields:
        field = aqt.mw.col.models.new_field(i)
        aqt.mw.col.models.add_field(new_model, field)
    # Add card_types
    for card_type in card_types:
        template = aqt.mw.col.models.new_template(card_type['name'])
        template['qfmt'] = card_type['front']
        template['afmt'] = card_type['back']
        aqt.mw.col.models.add_template(new_model, template)
    aqt.mw.col.models.add(new_model)

def _reload_config():
    utils.reload_config()
    global config_delimiter, config_css_name, config_tmpl_ext
    config_delimiter = utils.cfg("delimiter")
    config_css_name = utils.cfg("cssName")
    config_tmpl_ext = utils.cfg("tmplExt")

def import_tmpls():
    root = gui.get_dir()
    if not root: return
    _reload_config()

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
            update_model(
                model = model,
                css = css,
                card_types = card_types,
                fields = fields)
        # If the model doesn't exist, create it
        else:
            create_model(
                name = note_type_name,
                fields = fields,
                card_types = card_types,
                css = css)


def export_tmpls():
    root = gui.get_dir()
    if not root: return
    _reload_config()

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
    gui.notify("exported (Template: {} from NoteType:{})".format(count_template, count_notetype))
