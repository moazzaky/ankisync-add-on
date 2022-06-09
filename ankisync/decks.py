# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

import logging
from anki.decks import DeckDict, DeckId
from aqt import mw
from typing import Union
from .exceptions import ExistsError


def change_deck_id(existing_anki_deck_id, new_anki_deck_id) -> bool:

    deck = mw.col.decks.get(existing_anki_deck_id, False)

    if deck is None:
        raise KeyError("deck does not exist")

    try:
        mw.col.db.execute("UPDATE decks SET id=? WHERE id=?", new_anki_deck_id, existing_anki_deck_id)
    except:
        return False

    try:
        mw.col.db.execute("UPDATE cards SET did=? WHERE did=?", new_anki_deck_id, existing_anki_deck_id)

    except:
        # fixme: might need to change the ID back...eek
        return False

    # refresh the GUI as the ids have now changed!
    # mw.taskman.run_on_main(lambda: mw.deckBrowser.refresh())

    return True


def create(anki_deck_id: int, deck_name: str, deck_description: str) -> Union[DeckDict, None]:
    # check if already exists, if so, full stop
    deck = mw.col.decks.get(anki_deck_id, False)
    deck_by_name = mw.col.decks.by_name("AnkiSync::" + deck_name)

    if deck or deck_by_name is not None:
        raise ExistsError("deck already exists")  # parent will likely fail or rename/reid existing deck

    # create deck
    deck_id = mw.col.decks.id("AnkiSync::" + deck_name, True)

    if deck_id is None:
        raise Exception("anki could not create deck by name")  # anki couldn't make the deck for whatever reason

    # time to change the ID to an AnkiSync friendly one
    try:
        mw.col.db.execute("UPDATE decks SET id=? WHERE id=?", anki_deck_id, deck_id)
    except:
        # fixme: narrow exception
        raise Exception("anki could not modify deck id")

    # finally, lets get the deck by its new ID and change its description
    deck = mw.col.decks.get(anki_deck_id)

    if deck is None:
        raise KeyError(f"anki could not find deck by new deck id {anki_deck_id}")

    deck['desc'] = deck_description

    try:
        mw.col.decks.save(deck)
    except:
        # fixme: narrow exception
        raise Exception("anki could not save deck")

    # fixme: need to add mw.deckBrowser.refresh(), causes crash if called here due to Qt involvement

    logging.info('Created a new deck.')
    return deck


def create_root_deck():
    mw.col.decks.id("AnkiSync")


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


# returns deck | None
def get_deck_by_name(name):
    deck = mw.col.decks.by_name("AnkiSync::" + name)

    return deck

