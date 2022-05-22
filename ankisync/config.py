# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

import os
from aqt import mw

"""
config.py

Instructions
- Only use for CONSTANTS
"""

from pathlib import Path

APP_NAME = "AnkiSync"
BASE_URL = "https://ankisync.com/"
# USER_FILES_PATH = os.path.join(mw.pm.addonFolder(), "AnkiSync")  # Path(__file__).parent.joinpath('user_files')
ADDON = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ADDON)
USER_FILES = os.path.join(ROOT, 'user_files')

