# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.


import aqt


# After weeks of running GUIs incorrectly causing crashes...turns out Anki has a build in main thread checker!
# https://addon-docs.ankiweb.net/background-ops.html
def run_in_main_thread(anonymous_function):
    if aqt.mw.inMainThread():
        anonymous_function()
    else:
        aqt.mw.taskman.run_on_main(lambda: aqt.mw.progress.timer(0, anonymous_function, False))
