# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

from aqt.qt import (
QWidget, QVBoxLayout, QPushButton, QProgressBar, QTextEdit
)

from ..config import APP_NAME


class DebugWidget(QWidget):

    def __init__(self):
        super().__init__()

        # setup widget
        self.resize(600, 480)
        self.setWindowTitle(APP_NAME + ' - Debug')
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # setup layout content
        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.close)
        self.text_edit = QTextEdit()
        # self.text_edit.setDisabled(True)
        self.text_edit.setStyleSheet('background-color: rgb(255, 255, 255);')

        # setup layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.close_button)
        self.setLayout(self.layout)

    def append_text_edit(self, value):
        self.text_edit.append(str(value))
        # self.text_edit.append('\n')

    def clear_text_edit(self):
        self.text_edit.clear()


debug_widget = DebugWidget()
# debug_widget.show()
