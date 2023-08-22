import os
import json
import aqt
import logging
from . import utilities

# key names used by Anki
key_name_anki_model_css = "css"
key_name_anki_model_fields = "flds"
key_name_anki_model_templates = "tmpls"
key_name_anki_model_template_name = "name"
key_name_anki_model_template_front = "qfmt"
key_name_anki_model_template_back = "afmt"

def update_fields(model, new_fields, log_text):
  # Remove existing fields that don't exist in the new list of fields
  model_fields = model['flds']
  # We create a list containing the name of the existing fields in the
  # model, because we are not iterating through the list since we use
  # .remove() from the list
  model_field_names = [x['name'] for x in model_fields]
  for model_field_name in model_field_names:
    if model_field_name not in new_fields:
      model_field = next((item for item in model_fields if item['name'] == model_field_name), None)
      model_fields.remove(model_field)
      log_text.add_line(f"Field {model_field['name']} has been removed")
  # Iterate through the new field names and create them if they don't exist in the model
  for new_field_name in new_fields:
    existing_field = next((item for item in model_fields if item['name'] == new_field_name), None)
    if existing_field:
      continue
    new_field = aqt.mw.col.models.new_field(new_field_name)
    aqt.mw.col.models.add_field(model, new_field)
    log_text.add_line(f"Field {new_field_name} has been created")
  # At this point, the existing fields and the new fields have the
  # same number of elements, but the elements might not be sorted
  # according to the list of new fields.
  #
  # Sort the fields
  counter = 0
  for new_field_name in new_fields:
    field_dictionary = next((item for item in model_fields if item['name'] == new_field_name), None)
    aqt.mw.col.models.reposition_field(model, field_dictionary, counter)
    counter = counter + 1

def update_model(model, fields, card_types, css, log_text):
    # Update CSS
    model[key_name_anki_model_css] = css
    # Update fields
    update_fields(model, fields, log_text)
    # Update templates
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
    # Save changes
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
