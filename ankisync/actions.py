# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

"""
Actions are called by the GUI.
"""

from . import api as api
from . import sync
import socket


# sync.py
def start_sync(progress_callback):
    return sync.flashcards(progress_callback)


def login(email, password, progress_callback):
    return api.post_access_token(email, password, socket.gethostname())

