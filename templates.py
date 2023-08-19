import os
from os import path

from aqt import mw as window

from . import gui, utils

# key names used by Anki
key_name_anki_model_css = "css"
key_name_anki_model_templates = "tmpls"
key_name_anki_model_template_name = "name"
key_name_anki_model_template_front = "qfmt"
key_name_anki_model_template_back = "afmt"

# config
_delimiter: str = "```\n"
_css_name: str = "style.css"
_tmpl_ext: str = ""
_merge_css: bool = False


def _reload_config():
    utils.reload_config()
    global _delimiter, _css_name, _tmpl_ext, _merge_css
    _delimiter = utils.cfg("delimiter")
    _css_name = utils.cfg("cssName")
    _tmpl_ext = utils.cfg("tmplExt")
    _merge_css = utils.cfg("mergeCSS")


def import_tmpls():
    root = gui.get_dir()
    if not root: return
    _reload_config()

    notetypes = [item for item in os.listdir(root) if os.path.isdir(path.join(root, item))]

    global_css = None
    file = path.join(root, _css_name)
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            global_css = f.read()

    count_notetype = 0
    count_template = 0
    count_no_css = 0
    for name in notetypes:
        nt = window.col.models.byName(name)
        if not nt: continue

        count = 0
        file = path.join(root, name, _css_name)
        css = None
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                css = f.read()
        if global_css and css:
            nt[key_name_anki_model_css] = global_css + css if _merge_css else css
        elif global_css or css:
            nt[key_name_anki_model_css] = css if css else global_css
        else:
            count_no_css += 1

        for tmpl in nt.get(key_name_anki_model_templates, []):
            if key_name_anki_model_template_name not in tmpl:
                continue
            file_path_front = path.join(root, name, tmpl[key_name_anki_model_template_name], 'front.html')
            file_path_back = path.join(root, name, tmpl[key_name_anki_model_template_name], 'back.html')
            if os.path.exists(file_path_front):
                with open(file_path_front, "r", encoding="utf-8") as f:
                    tmpl[key_name_anki_model_template_front] = f.read()
                count += 1
            if os.path.exists(file_path_back):
                with open(file_path_back, "r", encoding="utf-8") as f:
                    tmpl[key_name_anki_model_template_back] = f.read()
                count += 1
        try:
            window.col.models.save(nt)
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
    for nt in window.col.models.all():
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
        notetype_path = path.join(root, notetype_name_stripped)
        os.makedirs(notetype_path, exist_ok=True)
        if key_name_anki_model_css in nt:
            with open(path.join(notetype_path, _css_name), "w", encoding="utf-8") as f:
                f.write(nt[key_name_anki_model_css])
        for tmpl in nt.get(key_name_anki_model_templates, []):
            try:
                tmpl_name = tmpl.get(key_name_anki_model_template_name)
            except KeyError:
                gui.show_error("A template in notetype \"{}\" has no name!!".format(notetype_name))
                continue
            # file_path_dir stores the name of the directory for a card type
            file_path_dir = path.join(notetype_path, tmpl_name) + '/'
            if not os.path.isdir(file_path_dir):
                os.makedirs(file_path_dir)
            file_path_front = path.join(file_path_dir, 'front.html')
            file_path_back = path.join(file_path_dir, 'back.html')
            if key_name_anki_model_template_front in tmpl:
                with open(file_path_front, "w", encoding="utf-8") as f:
                    f.write(tmpl[key_name_anki_model_template_front])
            if key_name_anki_model_template_front in tmpl:
                with open(file_path_back, "w", encoding="utf-8") as f:
                    f.write(tmpl[key_name_anki_model_template_back])
            count_template += 1
        count_notetype += 1
    gui.notify("exported (Template: {} from NoteType:{})".format(count_template, count_notetype))
