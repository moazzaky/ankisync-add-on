# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

import os
import re
from anki.utils import checksum
import urllib.request
from urllib.parse import unquote
from aqt.qt import *
import hashlib

from aqt import mw


def compare_media_lists(self):
    return None

def get_cards_media_list(self):
    return None

def get_local_media_list(self):
    return None

def get_root_dir(self):
    return None


# todo: may need to multithread? idk
def retrieve_media_via_url(url):
    """Download file into media folder and return local filename or None."""
    req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (compatible; Anki)'})
    resp = urllib.request.urlopen(req)
    # ct = resp.info().getheader("content-type")
    filecontents = resp.read()

    # strip off any query string
    url = re.sub(r"\?.*?$", "", url)
    path = str(url.encode("utf8"), "utf8")
    fname = os.path.basename(path)

    print(fname)

    print(filecontents)

    return mw.col.media.write_data(fname, filecontents)


def _importStaticMedia(self) -> None:
    # Import any '_foo' prefixed media files regardless of whether
    # they're used on notes or not
    dir = self.src.media.dir()
    if not os.path.exists(dir):
        return
    for fname in os.listdir(dir):
        if fname.startswith("_") and not self.dst.media.have(fname):
            self._writeDstMedia(fname, self._srcMediaData(fname))
