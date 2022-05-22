# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# from anki.stdmodels import addBasicModel, addClozeModel
from aqt import mw
from typing import cast

# cloze and basic models

# from anki.stdmodels import addBasicModel, addClozeModel

# m = mw.col.models.new("test123")


# field = mw.col.models.newField("test")
# mw.col.models.addField(m, field)

# template = mw.col.models.new_template("test123")
# mw.col.models.add_template(m, template)

# mw.col.models.add(m)
# mw.col.models.save(test)


# https://github.com/ankitects/anki/blob/98a4a1927a8e781a1c0b4a297caa8e86134ac027/pylib/anki/importing/mnemo.py

def create_basic_model():

    # check if model already exists
    existing_model = mw.col.models.byName('AnkiSync - Basic')

    if existing_model:
        return


def create_custom_cloze_model():

    # check if model already exists
    existing_model = mw.col.models.byName('AnkiSync - Cloze')

    if existing_model:
        return

    # start new model
    new_model = mw.col.models.new("AnkiSync - Cloze")

    # fields
    front_field = mw.col.models.newField("_front")
    back_field = mw.col.models.newField("_back")
    updated_at_field = mw.col.models.new("_updated_at")
    id_field = mw.col.models.new("_id")


def create():
    new_model = mw.col.models.new("AnkiSync")

    # add fields
    notes_field = mw.col.models.newField("notes")
    front_field = mw.col.models.newField("_front")
    back_field = mw.col.models.newField("_back")
    updated_at_field = mw.col.models.new("_updated_at")
    id_field = mw.col.models.new("_id")

    mw.col.models.addField(new_model, notes_field)
    mw.col.models.addField(new_model, front_field)
    mw.col.models.addField(new_model, back_field)
    mw.col.models.addField(new_model, updated_at_field)
    mw.col.models.addField(new_model, id_field)

    template = mw.col.models.newTemplate("Basic")
    template["qfmt"] = "{{_front}}"  # question side
    template["afmt"] = (
            cast(str, template["qfmt"])
            + """\n\n<hr id=answer>\n\n\{{_back}}<br>\n{{notes}}"""
    )  # answer side

    # add template
    mw.col.models.addTemplate(new_model, template)

    # add model
    mw.col.models.add(new_model)

    print(new_model)

