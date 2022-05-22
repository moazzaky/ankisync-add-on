# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# third party
from aqt import mw
import traceback
import json

# local
#from .dataclasses.deck import DataClassDeck


# Receives ankisync_id, name, and updated at. Needs to create local anki deck to get id to fully sync.
from .widgets.debug_widget import debug_widget


def create(name, description):

    # check if already exists, if so, full stop
    deck = mw.col.decks.byName("AnkiSync::" + name)

    # todo: add better handling instead of just returning None
    if deck:
        return None

    # since we know the deck doesnt already exist, lets now create it
    # first we initialize the deck and then
    # todo: ? try except
    deck_id = mw.col.decks.id("AnkiSync::" + name, True)
    deck = mw.col.decks.get(deck_id)

    # todo: check if deck was created

    deck['desc'] = description

    # refresh deck UI
    # todo: need to add mw.deckBrowser.refresh(), causes crash if called here

    return deck


def create_root_deck():
    mw.col.decks.id("AnkiSync")


# returns deck | None
def get(name):
    deck = mw.col.decks.byName("AnkiSync::" + name)

    return deck


# returns deck | None
def get_root_deck():
    return mw.col.decks.by_name("AnkiSync")


def get_root_deck_child_ids():

    root_deck = get_root_deck()

    if root_deck is None:
        return None

    tuples = mw.col.decks.children(root_deck["id"])

    if tuples is None:
        return None

    # pops out all child ids
    return [x[1] for x in tuples]


def remove(name):
    deck_id = mw.col.decks.id_for_name(name)

    mw.col.decks.rem(deck_id)


####################




def update(anki_id, ankisync_id, name, updated_at):
    anki_deck = mw.col.decks.get(anki_id)

    if anki_deck is None:
        return

    anki_deck['name'] = name

    deck = DataClassDeck(ankisync_id, anki_id, name, updated_at)

    deck.update()
    # deck['updated_at'] = updated_at

    mw.col.decks.save(anki_deck)

# deletes only the reference to the deck for when a user unsubscribes on ankisync.com
def soft_delete(self) -> bool:

    return None


# deprecated
def get_synced_decks() -> any:
    try:
        return []

    except Exception as error:
        debug_widget.append_text_edit(traceback.format_exc())
        # todo: proper error handling
        return False



    if decks is None:
        return []
    else:
        return decks


# deprecated
def _get_flashcards_for_deck(self, deck_id):
    cids = mw.col.decks.cids(deck_id)

    cards = [mw.col.getCard(cid) for cid in cids]

    notes = [mw.col.getNote(card.nid) for card in cards]

    flashcards = []
    for note in notes:
        if all(elem in mw.col.models.fieldNames(note.model()) for elem in ['_id', '_updated_at', '_front', '_back', '_notes']):
            flashcards.append(note)

    return flashcards

