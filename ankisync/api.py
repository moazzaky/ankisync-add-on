# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is not distributed under the AGPL license as it is a direct interface with ankisync.com. All rights are
# reserved.

# third party imports
import json
import requests

# local imports
from . import utils
from .config import BASE_URL
from .gui import gui
from .widgets.debug_widget import debug_widget


def post_access_token(email, password, device_name):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    url = BASE_URL + "api/access_tokens"

    json_payload = {"email": email, "password": password, "device_name": device_name}

    x = requests.post(url, json.dumps(json_payload), headers=headers)

    if x.status_code == 200:
        response_json = x.json()

        if response_json.get('success'):
            access_token = response_json.get('data', {}).get('access_token')
            # returns flashcards in ankisync format
            return {
                "success": True,
                "access_token": access_token
            }
    elif x.status_code == 422:
        return {
            "success": False,
            "message": "Invalid email or password. Please try again."
        }
    else:
        # post error to debug widget
        debug_widget.append_text_edit(x.status_code)
        debug_widget.append_text_edit(x.json())
        return {
            "success": False,
            "message": "An unknown error occurred. Please try again later."
        }


def post_remote_deck(anki_id, ankisync_id):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + utils.access_token.get(),
        'Content-Type': 'application/json'
    }

    url = BASE_URL + "api/remote_decks"

    json_payload = {"anki_deck_id": anki_id, "deck_id": ankisync_id}

    x = requests.post(url, json.dumps(json_payload), headers=headers)

    # debug_widget.append_text_edit(x.json())

    try:
        response_json = x.json()

        return response_json
    except:
        debug_widget.append_text_edit("Raw post_remote_deck response for debugging..." + str(x.raw))
        return None


def put_remote_deck(anki_deck_id, ankisync_deck_id):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + utils.access_token.get(),
        'Content-Type': 'application/json'
    }

    url = BASE_URL + "api/remote_decks"

    json_payload = {"anki_deck_id": anki_deck_id, "deck_id": ankisync_deck_id, "last_synced_at": True}

    x = requests.put(url, json.dumps(json_payload), headers=headers)

    ##debug_widget.append_text_edit(x.json())

    response_json = x.json()

    return response_json


def get_deck_by_id(deck_id):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + utils.access_token.get(),
        'Content-Type': 'application/json'
    }
    url = BASE_URL + 'api/decks/' + deck_id

    # x = requests.post(url, json.dumps({"decks": decks}), headers=headers)
    x = requests.get(url, None, headers=headers)

    if x.status_code == 200:
        response_json = x.json()

        if response_json.get('success'):
            deck = response_json.get('data', {}).get('deck')
            # returns flashcards in ankisync format
            return deck
    else:
        # Exception('Failed to get flashcards from server.')
        return None


# get synced decks from conf which is synced to remote anki server
def get_subscribed_decks():
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + utils.access_token.get(),
        'Content-Type': 'application/json'
    }
    url = BASE_URL + 'api/me/decks'

    # x = requests.post(url, json.dumps({"decks": decks}), headers=headers)
    x = requests.get(url, None, headers=headers)

    if x.status_code == 200:
        response_json = x.json()

        if response_json.get('success'):
            decks = response_json.get('data', {}).get('decks')
            # debug_widget.append_text_edit(decks)
            # returns flashcards in ankisync format
            return decks
    elif x.status_code == 401:
        # Exception('Failed to get flashcards from server.')
        #debug_widget.append_text_edit(x.status_code)
        #debug_widget.append_text_edit(x.json())
        utils.access_token.set(None)
        #debug_widget.append_text_edit(gui.access_token)
        return None
    else:
        debug_widget.append_text_edit(x.status_code)
        debug_widget.append_text_edit(x.json())


# get synced decks from conf which is synced to remote anki server
def get_remote_decks():
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + utils.access_token.get(),
        'Content-Type': 'application/json'
    }
    url = BASE_URL + 'api/remote_decks'

    # x = requests.post(url, json.dumps({"decks": decks}), headers=headers)
    x = requests.get(url, None, headers=headers)

    if x.status_code == 200:
        response_json = x.json()

        if response_json.get('success'):
            remote_decks = response_json.get('data', {}).get('remote_decks')
            # debug_widget.append_text_edit(decks)
            # returns flashcards in ankisync format
            return remote_decks
    elif x.status_code == 401:
        # Exception('Failed to get flashcards from server.')
        #debug_widget.append_text_edit(x.status_code)
        #debug_widget.append_text_edit(x.json())
        utils.access_token.set(None)
        #debug_widget.append_text_edit(gui.access_token)
        return None
