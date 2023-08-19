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

def update_note_type(model, fields, templates, css):
    current_templates = model['tmpls']
    for template_to_edit_or_add in templates:
        index = next((i for i, item in enumerate(current_templates) if item['name'] == template_to_edit_or_add['name']), None)
        # In this conditional, we shouldn't write "if index:", because
        # when the index is 0, it will evaluate to False, when index
        # is 0, we want to evaluate to True.
        if index != None:
            current_templates[index]['qfmt'] = template_to_edit_or_add['front']
            current_templates[index]['afmt'] = template_to_edit_or_add['back']
        else:
            template = aqt.mw.col.models.new_template(template_to_edit_or_add['name'])
            template['qfmt'] = template_to_edit_or_add['front']
            template['afmt'] = template_to_edit_or_add['back']
            aqt.mw.col.models.add_template(model, template)

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

    notetypes = [item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item))]

    count_notetype = 0
    count_template = 0
    count_no_css = 0
    for name in notetypes:
        nt = aqt.mw.col.models.byName(name)
        if not nt:
            continue

        count = 0
        # Iterate through all directories that exist inside the
        # directory of a note type. Each directory correspond to a
        # card type and generally contain two files: front.html and
        # back.html.
        file_path_dir_card_types = [os.path.join(root, name, x)
                                   for x in os.listdir(os.path.join(root, name))
                                   if os.path.isdir(os.path.join(root, name, x))]
        # Collect all card types
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
        # Update the css, fields, card type of the note type
        update_note_type(nt, '', card_types, '')
        try:
            aqt.mw.col.models.save(nt)
        except Exception:
            gui.show_error("note type \"{}\" contains errors!!".format(name))
            continue
        count_notetype += 1
        count_template += count
    gui.notify("imported (Template: {}, CSS: {} from NoteType:{})".format(count_template, count_notetype - count_no_css,
                                                                          count_notetype))


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
