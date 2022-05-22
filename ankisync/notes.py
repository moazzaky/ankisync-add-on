# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

from .libraries.bs4 import BeautifulSoup
from aqt import mw

from . import media
from .widgets.debug_widget import debug_widget

# save guid for future use


# creates a new note for CURRENT deck
def create(anki_deck_id, ankisync_flashcard_id, front, back, tags, updated_at):

    # parse front to determine if basic, cloze, or other

    # parse img tags to download + convert
    soup_front = BeautifulSoup(front, features="html.parser")
    soup_back = BeautifulSoup(back, features="html.parser")

    for img in soup_front.findAll('img'):
        media.retrieve_media_via_url('http://192.168.1.14' + img['src'])
        img['src'] = img['src'].replace("/storage/", "")

    for img in soup_back.findAll('img'):
        media.retrieve_media_via_url('http://192.168.1.14' + img['src'])
        img['src'] = img['src'].replace("/storage/", "")

    front = str(soup_front)
    back = str(soup_back)

    model_id = mw.col.models.id_for_name('AnkiSync')

    model = mw.col.models.get(model_id)

    if model is None:
        return False

    #mw.col.models.set_current(model)

    # debug_widget.append_text_edit(mw.col.models.current())

    # false as it should pick the current model, not the model for the current deck
    note = mw.col.new_note(model)

    note['_extra'] = ''
    note['_front'] = front
    note['_back'] = back
    note['_updated_at'] = updated_at
    note['_id'] = ankisync_flashcard_id
    note.guid = ankisync_flashcard_id
    note.model()["did"] = anki_deck_id

    note.tags = []

    for tag in tags:
        note.add_tag(tag['name'])

    # note.id = id, cannot set as uuid, has to be int

    # model = mw.col.models.id_for_name("AnkiSync - Basic")

    try:
        mw.col.add_note(note, anki_deck_id)
    except:
        print("Error adding note")

    return True


def update(deck_id, ankisync_id, front, back, tags, updated_at) -> bool:
    deck = mw.col.decks.get(deck_id)

    if deck is None:
        return False
    # debug_widget.append_text_edit('Updating note in deck')
    # debug_widget.append_text_edit(deck)

    # find notes matching this criteria -> returns an array of note ids
    note_ids = mw.col.find_notes('"deck:' + deck['name'] + '" ' + '"_id:' + ankisync_id + '"')

    if len(note_ids) <= 0:
        return create(deck_id, ankisync_id, front, back, tags, updated_at)
    else:
        note_id = note_ids[0]

    note = mw.col.getNote(note_id)

    if note is None:
        return False

    # parse img tags to download + convert
    soup_front = BeautifulSoup(front, features="html.parser")
    soup_back = BeautifulSoup(back, features="html.parser")

    for img in soup_front.findAll('img'):
        media.retrieve_media_via_url('http://192.168.1.14' + img['src'])
        img['src'] = img['src'].replace("/storage/", "")

    for img in soup_back.findAll('img'):
        media.retrieve_media_via_url('http://192.168.1.14' + img['src'])
        img['src'] = img['src'].replace("/storage/", "")

    front = str(soup_front)
    back = str(soup_back)

    note['_front'] = front
    note['_back'] = back
    note['_updated_at'] = updated_at

    note.tags = []

    for tag in tags:
        note.addTag(tag['name'])

    note.flush()

    return True


def get_by_ankisync_id(id):
    return mw.col.find_notes("_id:" + id)


def get_by_id(id):
    return mw.col.getNote(id)  # or mw.col.find_notes("nid:" + id)




