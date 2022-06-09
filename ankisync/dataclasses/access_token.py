# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

"""
access_token.py

Notes
- Access tokens are stored on ONE device only via the user_files folder
    - Does not sync across devices
    - Does persistent across addon updates
"""

# Standard library imports
import json
from dataclasses import dataclass
from typing import Union
from pathlib import Path

# Third party imports
from aqt.utils import showInfo

# Local application imports
from ..constants import USER_FILES


@dataclass
class DataClassAccessToken:
    access_token: Union[str, None] = None

    # returns access token or none if not set
    def get(self) -> Union[str, None]:

        if self.access_token is not None:
            return self.access_token
        else:
            # get local access token
            try:
                with open(str(USER_FILES) + '\\access_token.json') as json_file:
                    obj = json.load(json_file)
            except Exception as error:
                # todo: proper error handling
                return None

            if obj['access_token'] is not None:
                return obj['access_token']
            else:
                return None

    # returns true if access token is successfully saved
    # todo: figure out if this works on iOS... look at the path
    def set(self, access_token) -> bool:
        try:
            with open(str(USER_FILES) + '\\access_token.json', 'a+') as outfile:
                outfile.truncate(0)
                json.dump({"access_token": access_token}, outfile)

            self.access_token = access_token

            return True
        except Exception as error:
            # todo: proper error handling
            showInfo(str(error))
            return False

    def delete(self) -> bool:
        # eliminate "cached" access token from this class
        self.access_token = None

        access_token_file = Path(str(USER_FILES) + '\\access_token.json')

        try:
            if not access_token_file.exists():
                return False

            access_token_file.unlink()

            return True
        except Exception as error:
            # todo: proper error handling
            showInfo(str(error))
        return False

