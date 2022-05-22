# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is not distributed under the AGPL license as it is a direct interface with ankisync.com. All rights are
# reserved. 

def post_access_token(email, password, device_name):
    return {
        "success": True,
        "access_token": "token"
    }


def get_deck_by_id(deck_id):
    return None


def get_user_decks():
    return None