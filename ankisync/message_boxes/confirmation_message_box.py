# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

from aqt.qt import QMessageBox


class ConfirmationMessageBox(QMessageBox):

    def __init__(self, question_title, question_text):
        super().__init__()

        # self.StandardButton.Yes

        self.question_title = question_title

        self.question_text = question_text

        # setup question, if we need to can use aqt.qt.qtmajor
        self.response = self.question(self, self.question_title, self.question_text, self.StandardButton.Yes | self.StandardButton.No)
