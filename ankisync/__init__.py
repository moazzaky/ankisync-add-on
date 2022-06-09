# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.


import sys

# if 'pytest' not in sys.modules:
from aqt import mw

from .gui import Gui
from . import decks
from . import exceptions
from . import logger


class AnkiSync:
    def __init__(self):

        self.decks = decks
        self.gui = Gui()


mw.ankisync = ankisync = AnkiSync()

