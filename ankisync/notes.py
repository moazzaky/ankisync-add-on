# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.
from typing import Union

import logging
from .libraries.bs4 import BeautifulSoup
from aqt import mw
from anki.notes import Note

from . import media

logger = logging.getLogger('ankisync.notes')
# from .widgets.debug_widget import debug_widget

# save guid for future use


# creates a new note for CURRENT deck
def create(anki_deck_id, anki_flashcard_id, ankisync_flashcard_id, front, back, extra, tags, updated_at):

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

    note['_extra'] = extra
    if extra is None:
        note['_extra'] = ""

    note['_front'] = front
    note['_back'] = back
    note['_updated_at'] = updated_at
    note['_id'] = ankisync_flashcard_id
    note.guid = ankisync_flashcard_id
    note.note_type()["did"] = anki_deck_id  # fixme: what does this even do

    note.tags = []

    for tag in tags:
        note.add_tag(tag)

    # note.id = id, cannot set as uuid, has to be int

    # model = mw.col.models.id_for_name("AnkiSync - Basic")

    try:
        mw.col.add_note(note, anki_deck_id)
    except Exception as e:
        logger.debug("Could not create note " + str(e))

    is_note_id_changed = change_note_id(note, anki_flashcard_id)

    if is_note_id_changed is False:
        return False

    return True


def update(deck_id, anki_id, ankisync_id, front, back, extra, tags, updated_at) -> bool:
    deck = mw.col.decks.get(deck_id)

    if deck is None:
        return False
    # debug_widget.append_text_edit('Updating note in deck')
    # debug_widget.append_text_edit(deck)

    # find notes matching this criteria -> returns an array of note ids
    note_ids = mw.col.find_notes('nid:' + str(anki_id))

    # creates new note if doesnt exist
    if len(note_ids) <= 0:
        logger.debug("could not find note so will create one " + str(anki_id))
        # e(anki_deck_id, anki_flashcard_id, ankisync_flashcard_id, front, back, tags, updated_at):
        return create(deck_id, anki_id, ankisync_id, front, back, extra, tags, updated_at)
    else:
        note_id = note_ids[0]

    # logger.info("Finding note to update via ID " + str(note_id))
    note = mw.col.get_note(note_id)

    if note is None:
        logger.debug("Could not find note via ID " + str(note_id))
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
    note['_extra'] = extra
    if extra is None:
        note['_extra'] = ""

    note['_updated_at'] = updated_at

    note.tags = []

    # logger.info("Adding tags to note " + str(tags))

    for tag in tags:
        note.addTag(tag)

    logger.debug("Updating note ID " + str(note.id) + " " + repr(note))

    #mw.col.update_note(note)
    note.flush()

    return True


def get_by_ankisync_id(id):
    return mw.col.find_notes("_id:" + id)


# def get_by_id(id):
    # return mw.col.get_note(id)  # or mw.col.find_notes("nid:" + id)


def change_note_id(note, new_id) -> bool:

    cards = note.cards()

    try:
        mw.col.db.execute("""update notes set id=? where id=? """, new_id, note.id)
    except:
        return None

    for c in cards:
        c.nid = new_id
        c.usn = mw.col.usn()
        c.flush()
