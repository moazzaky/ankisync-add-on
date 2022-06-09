# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.
import logging
from datetime import datetime

from aqt.utils import showInfo

from . import api
from . import decks
from . import models
from . import notes


class Sync:

    def __init__(self, parent):
        # used for filtering
        self.errors = []
        self.decks_name_conflicts = []
        self.decks_to_add = []
        self.decks_to_update = []
        self.decks_to_soft_delete = []
        self.decks_to_mark_unsubscribed = []

        self.all_remote_decks = None
        self.matched_decks = []  # decks match here on the local client
        self.subscribed_decks = None  # decks the user is ACTIVELY subscribed to server side
        self.sync_widget = parent

        self.local_deck_ids = []

        self.logger = logging.getLogger('ankisync.sync')

    def add_decks(self):
        # add decks
        if self.decks_to_add:
            for deck_to_add in self.decks_to_add:
                deck = decks.get_deck_by_name(deck_to_add['name'])

                if deck:
                    # already exists... thus cannot add, uh oh!
                    self.decks_name_conflicts.append(deck_to_add)
                else:
                    deck = api.get_deck_by_id(deck_to_add['ankisync_id'])

                    # create deck
                    anki_deck = decks.create(deck_to_add["anki_id"], deck_to_add['name'], deck_to_add['description'])

                    for flashcard in deck.flashcards:
                        notes.create(anki_deck['id'], flashcard['anki_id'], flashcard['external_id'], flashcard['front'],
                                     flashcard['back'], flashcard['extra'],
                                     flashcard['tags'], flashcard['updated_at'])

    def update_decks(self):
        # now to update decks
        for deck_to_update in self.decks_to_update:
            deck = api.get_deck_by_id(deck_to_update['external_id'])

            if deck is None:
                self.logger.debug('cannot find deck to update')
                return
            self.logger.debug('updating ' + str(len(deck.flashcards)) + ' flashcards')
            for flashcard in deck.flashcards:
                notes.update(deck.anki_id, flashcard['anki_id'], flashcard['external_id'], flashcard['front'], flashcard['back'], flashcard['extra'], flashcard['tags'], flashcard['updated_at'])

            # mark as updated
            api.put_deck(deck_to_update['external_id'])

    def determine_decks_to_add(self):
        # compare subscribed decks to matched, if not in, add
        for subscribed_deck in self.subscribed_decks:
            if any(subscribed_deck["anki_id"] == local_deck_id for local_deck_id in self.local_deck_ids) is not True:
                self.decks_to_add.append({
                    "anki_id": subscribed_deck["anki_id"],
                    "ankisync_id": subscribed_deck["external_id"],
                    "name": subscribed_deck["name"],
                    "description": subscribed_deck["description"],
                    "updated_at": subscribed_deck["updated_at"]
                })

    # determine which decks exist on both the server and client
    def determine_matched_decks(self):
        if self.subscribed_decks is not None:
            for deck in self.subscribed_decks:
                for local_deck_id in self.local_deck_ids:
                    if str(local_deck_id) == str(deck["anki_id"]):
                        self.matched_decks.append(deck)
                        break

    def determine_decks_to_update(self) -> None:
        if len(self.matched_decks) == 0:
            self.logger.debug("no matched decks")
            return

        for deck in self.matched_decks:
            self.logger.debug("last_sync_at" + str(deck['last_synced_at'] is None))
            if deck['last_synced_at'] is None:
                self.logger.debug("deck never been synced")
                self.decks_to_update.append(deck)
                continue

            should_update = datetime.strptime(deck["updated_at"], '%Y-%m-%dT%H:%M:%S.%fZ') > datetime.strptime(deck['last_synced_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            self.logger.debug("should_update" + str(should_update))
            if should_update:
                self.logger.debug("deck should be updated")
                self.decks_to_update.append(deck)

    def determine_unsubscribed_decks(self) -> None:
        for local_deck_id in self.local_deck_ids:
            if any(deck["anki_id"] == local_deck_id for deck in
                   self.matched_decks) \
                    is not True:
                self.decks_to_mark_unsubscribed.append(local_deck_id)

    def run(self, progress_callback):

        progress_callback.emit(('Starting sync...', 10))
        progress_callback.emit(('Verifying default settings.', 20))

        check_default_note_type()
        check_root_deck()

        self.local_deck_ids = decks.get_root_deck_child_ids()
        self.subscribed_decks = api.get_subscribed_decks()

        if self.subscribed_decks is None:
            progress_callback.emit(
                ('There are no decks to sync. Please go to AnkiSync.com and subscribe to some decks.', 100))
            return

        self.sync_widget.set_remote_decks(self.subscribed_decks)

        self.determine_matched_decks()
        self.logger.debug("Matched decks: " + str(len(self.matched_decks)))
        self.determine_decks_to_add()
        self.determine_decks_to_update()
        self.logger.debug("Decks to update: " + str(len(self.decks_to_update)))
        self.determine_unsubscribed_decks()

        if len(self.decks_to_add) > 0:
            progress_callback.emit(('Adding ' + str(len(self.decks_to_add)) + ' decks.', 25))

        self.add_decks()

        # tell user what to do about naming conflicts
        if len(self.decks_name_conflicts) > 0:
            progress_callback.emit(('Naming conflicts: ' + str(len(self.decks_name_conflicts)) + '.', 30))

            progress_callback.emit(('<b>A deck already exists with the same name as the new deck to be created. '
                                    'Please move the following decks from the AnkiSync parent deck: </b>', 30))
            for deck_name_conflict in self.decks_name_conflicts:
                progress_callback.emit((str(deck_name_conflict["name"]), 30))

        progress_callback.emit(("Updating decks..." + str(len(self.decks_to_update)), 50))
        self.update_decks()

        progress_callback.emit(('Done.', 75))

        progress_callback.emit((None, 100))

        return True


def check_default_note_type() -> bool:

    default_model = models.check_if_default_note_type_exists()

    if default_model is False:
        # debug_widget.append_text_edit("Creating default note type...")
        models.create_default_note_type()

    if models.validate_default_note_type() is False:
        return False

    # update template and css every time
    models.update_default_note_type()

    return True


def check_root_deck():
    # check if root "AnkiSync" deck actually exists
    root_deck = decks.get_root_deck()

    if root_deck is None:
        decks.create_root_deck()

