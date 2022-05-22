# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.


from datetime import datetime
from . import api as api
from . import decks
from . import models
from . import notes
from .widgets.debug_widget import debug_widget


# Everything to do with syncing
# Sync Flow
# 1.


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


class Sync:

    def __init__(self, parent):
        self.sync_widget = parent
        self.decks_name_conflicts = []
        self.decks_to_add = []
        self.decks_to_update = []
        self.decks_to_soft_delete = []
        self.decks_to_mark_missing = []
        self.decks_to_mark_unsubscribed = []

    def update_decks(self):
        # now to update decks
        for deck_to_update in self.decks_to_update:
            #_widget.append_text_edit("Grabbing ankisync deck by id: " + str(deck_to_update['ankisync_deck_id']))
            deck = api.get_deck_by_id(deck_to_update['ankisync_deck_id'])

            if deck is None:
                #debug_widget.append_text_edit("Unable to find deck by ankisync id.")
                return

            #debug_widget.append_text_edit("Updating flashcards " + str(len(deck['flashcards'])) + "...")

            for flashcard in deck['flashcards']:
                #debug_widget.append_text_edit(flashcard)
                notes.update(deck_to_update['anki_deck_id'], flashcard['external_id'], flashcard['front'],
                             flashcard['back'], flashcard['tags'], flashcard['updated_at'])

            #debug_widget.append_text_edit("Marking new sync date...")
            api.put_remote_deck(deck_to_update['anki_deck_id'], deck_to_update['ankisync_deck_id'])

    def run(self, progress_callback):

        progress_callback.emit(('Starting sync...', 10))
        progress_callback.emit(('Verifying default settings.', 20))

        check_default_note_type()
        check_root_deck()

        # determine which previously synced decks match here on the local client
        matched_decks = []

        # get all decks the user is ACTIVELY subscribed to
        subscribed_decks = api.get_subscribed_decks()

        self.sync_widget.set_remote_decks(subscribed_decks)

        # check if user is actually subscribed to anything
        if subscribed_decks is None:
            progress_callback.emit(
                ('There are no decks to sync. Please go to AnkiSync.com and subscribe to some decks!', 100))
            return

        # all decks successfully synced with Anki at some point (these can even be unsubscribed decks)
        remote_decks = api.get_remote_decks()  # anki_deck_id, deck_id

        # get all deck ids actually on this Anki client
        local_deck_ids = decks.get_root_deck_child_ids()

        if remote_decks is not None:  # checks if empty
            for local_deck_id in local_deck_ids:
                for remote_deck in remote_decks:
                    #debug_widget.append_text_edit(
                        #"Comparing decks... " + str(local_deck_id) + " and " + str(remote_deck["anki_deck_id"]))
                    if str(local_deck_id) == str(remote_deck["anki_deck_id"]):
                        matched_decks.append({
                            "anki_deck_id": local_deck_id,
                            "ankisync_deck_id": remote_deck["deck_id"],
                            "last_synced_at": remote_deck["last_synced_at"]
                        })

        #debug_widget.append_text_edit("Found matched decks: " + str(matched_decks))

        # compare subscribed decks to matched, if not in, add
        for subscribed_deck in subscribed_decks:
            if any(subscribed_deck["external_id"] == matched_deck["ankisync_deck_id"] for matched_deck in
                   matched_decks) is not True:
                self.decks_to_add.append({
                    "ankisync_deck_id": subscribed_deck["external_id"],
                    "name": subscribed_deck["name"],
                    "description": subscribed_deck["description"],
                    "updated_at": subscribed_deck["updated_at"],
                    "flashcards": subscribed_deck["flashcards"]
                })

        if len(self.decks_to_add) > 0:
            progress_callback.emit(('Adding ' + str(len(self.decks_to_add)) + ' decks.', 25))

        # add decks
        if self.decks_to_add:
            for deck_to_add in self.decks_to_add:
                deck = decks.get(deck_to_add['name'])

                if deck:
                    # already exists... thus cannot add, uh oh!
                    self.decks_name_conflicts.append(deck_to_add)
                else:
                    # create deck
                    deck = decks.create(deck_to_add['name'], deck_to_add['description'])

                    # debug_widget.append_text_edit(deck)
                    remote_deck = api.post_remote_deck(str(deck["id"]), deck_to_add["ankisync_deck_id"])

                    # check if deck already synced as remote_deck
                    if "message" in remote_deck and remote_deck["message"] == "Relationship already exists":
                        # decks.remove(deck_to_add['name'])
                        progress_callback.emit(('<b>' + deck_to_add[
                            'name'] + 'has been synced with the remote server before. Did you delete a deck or move '
                                      'it outside the AnkiSync folder? If so, you will need to update this on '
                                      'AnkiSync.com.</b>', 30))
                        progress_callback.emit(
                            ('<a href="https://ankisync.com/remote_decks">Click here to update</a>', 30))

                    #debug_widget.append_text_edit(
                        #"remote_deck" + str(deck["id"]) + " " + deck_to_add["ankisync_deck_id"])
                    #debug_widget.append_text_edit(remote_deck)

                    # add cards is successful
                    if remote_deck and remote_deck["success"]:
                        for flashcard in deck_to_add['flashcards']:
                            #debug_widget.append_text_edit("creating flashcard")
                            #debug_widget.append_text_edit(str(flashcard))
                            notes.create(deck['id'], flashcard['external_id'], flashcard['front'], flashcard['back'],
                                         flashcard['tags'], flashcard['updated_at'])
                            # TR.EDanITING_CLOZE_DELETION_CTRLANDSHIFTANDC
                        api.put_remote_deck(str(deck["id"]), deck_to_add["ankisync_deck_id"])

        # tell user what to do about naming conflicts
        if len(self.decks_name_conflicts) > 0:
            progress_callback.emit(('Naming conflicts: ' + str(len(self.decks_name_conflicts)) + '.', 30))

            progress_callback.emit(('<b>A deck already exists with the same name as the new deck to be created. '
                                    'Please move the following decks from the AnkiSync parent deck: </b>', 30))
            for deck_name_conflict in self.decks_name_conflicts:
                progress_callback.emit((str(deck_name_conflict["name"]), 30))

        # match subscribed to matched decks to determine decks to update
        for subscribed_deck in subscribed_decks:
            for matched_deck in matched_decks:
                #debug_widget.append_text_edit("")
                #debug_widget.append_text_edit("")
                #debug_widget.append_text_edit(subscribed_deck)
                #debug_widget.append_text_edit(matched_deck)
                #debug_widget.append_text_edit(
                #    datetime.strptime(subscribed_deck["updated_at"], '%Y-%m-%dT%H:%M:%S.%fZ') > datetime.strptime(
                #        matched_deck['last_synced_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))
                if subscribed_deck["external_id"] == matched_deck["ankisync_deck_id"] \
                        and datetime.strptime(subscribed_deck["updated_at"], '%Y-%m-%dT%H:%M:%S.%fZ') \
                        > datetime.strptime(matched_deck['last_synced_at'], '%Y-%m-%dT%H:%M:%S.%fZ'):
                    self.decks_to_update.append({
                        "anki_deck_id": matched_deck["anki_deck_id"],
                        "ankisync_deck_id": matched_deck["ankisync_deck_id"],
                        "updated_at": subscribed_deck["updated_at"],
                    })

        progress_callback.emit(("Updating decks...", 50))
        self.update_decks()

        for matched_deck in matched_decks:
            if any(subscribed_deck["external_id"] == matched_deck["ankisync_deck_id"] for subscribed_deck in
                   subscribed_decks) \
                    is not True:
                self.decks_to_mark_unsubscribed.append({
                    "anki_deck_id": matched_deck["anki_deck_id"],
                    "ankisync_deck_id": matched_deck["ankisync_deck_id"],
                })

        for remote_deck in remote_decks:
            if remote_deck["anki_deck_id"] not in local_deck_ids:
                self.decks_to_mark_missing.append({
                    "anki_deck_id": remote_deck["anki_deck_id"],
                    "ankisync_deck_id": remote_deck["deck_id"]
                })

        # for remote_deck in remote_decks:
        # if any(synced_deck['ankisync_id'] == deck['external_id'] for synced_deck in synced_decks) is not True:

        # todo: better way to handle unsubscribed decks
        #

        progress_callback.emit(('Done.', 100))

        return True


def flashcards(progress_callback):


    #debug_widget.append_text_edit("Remote decks: " + str(remote_decks))


    debug_widget.append_text_edit("Local deck ids: " + str(local_deck_ids))


    # mw.deckBrowser.refresh()

    # for deck_to_update in decks_to_update:
    return None


def _flashcards(progress_callback):
    # get local decks that have previously been synced
    synced_decks = api.get_remote_decks()

    if synced_decks is False:
        progress_callback.emit((100, 'Unable to sync due to an unknown error.'))
        return

    # debug_widget.append_text_edit(str(synced_decks))

    # check if any synced decks still exist, user could have manually deleted all of them
    # if synced_decks is None or len(synced_decks) == 0:
    # progress_callback.emit((100, 'You have no AnkiQueen decks.'))
    # todo: add button
    # progress_callback.emit((100, 'Click the browse decks button below to subscribe to a new deck.'))
    # return False

    # get removed decks that need to be synced (eid, name, updated_at)
    remote_decks = api.get_user_decks()

    # check if remote decks returned anything
    if remote_decks is None:
        progress_callback.emit((100, 'There are no decks to sync.'))
        return

    # todo: add last update time
    decks_to_add = []
    decks_to_update = []
    decks_to_soft_delete = []

    # determine decks we need to create
    for deck in remote_decks:
        if any(synced_deck['ankisync_id'] == deck['external_id'] for synced_deck in synced_decks) is not True:
            decks_to_add.append(deck)

    # determine decks we need to no longer sync
    for synced_deck in synced_decks:
        if any(synced_deck['ankisync_id'] == deck['external_id'] for deck in remote_decks) is not True:
            decks_to_soft_delete.append(synced_deck)

    # determine decks that already exist in anki and we want to sync
    for deck in remote_decks:
        for synced_deck in synced_decks:
            if synced_deck['ankisync_id'] == deck['external_id'] and deck['updated_at'] > synced_deck['updated_at']:
                synced_deck['flashcards'] = deck['flashcards']
                synced_deck['updated_at'] = deck['updated_at']
                synced_deck['name'] = deck['name']  # + ' (AnkiSync)'
                decks_to_update.append(synced_deck)

    progress_callback.emit((25, 'Adding ' + str(len(decks_to_add)) + ' decks.'))

    # add decks
    for deck_to_add in decks_to_add:
        deck = decks.create(deck_to_add['external_id'], deck_to_add['name'], deck_to_add['updated_at'])

        for flashcard in deck_to_add['flashcards']:
            notes.create(deck.anki_id, flashcard['external_id'], flashcard['front'], flashcard['back'],
                         flashcard['updated_at'])
            # TR.EDITING_CLOZE_DELETION_CTRLANDSHIFTANDC

    # update decks
    for deck in decks_to_update:
        for flashcard in deck['flashcards']:
            notes.update(deck['anki_id'], flashcard['external_id'], flashcard['front'], flashcard['back'],
                         flashcard['updated_at'])

        # "touch" updated_at, change name if renamed, using anki_id to identify deck; only occurs after updating notes
        decks.update(deck['anki_id'], deck['ankisync_id'], deck['name'],
                     deck['updated_at'])  # todo: fix so it updates, updated_at

    progress_callback.emit((50, 'Updating ' + str(len(decks_to_update)) + ' decks.'))

    # soft delete deck
    for deck in decks_to_soft_delete:
        return
        # decks.soft_delete(deck['anki_id'], deck['name'], deck[''])

    progress_callback.emit((75, 'Soft deleting ' + str(len(decks_to_soft_delete)) + ' decks.'))

    progress_callback.emit((100, 'Done.'))

    # mw.deckBrowser.refresh()

    # for deck_to_update in decks_to_update:
    return None


def media():
    return None


# return media to be updated?
def _update_deck_and_flashcards(anki_deck_id, ankiqueen_deck_id):
    # get deck which includes all flashcards
    deck = api.get_decks(ankiqueen_deck_id)

    # if deck is not None:

# note = mw.col.newNote()
# note.flush()
# mw.col.decks.select()
# deck_id = mw.col.decks.id("AnkiQueen", True)
# mw.deckBrowser.refresh()

# mw.col.decks.rename(deck, "new_name")
