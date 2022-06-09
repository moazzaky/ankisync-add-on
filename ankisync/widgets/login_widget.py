# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

from aqt.qt import (
    Qt,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStatusBar,
    QWidget,
)
from aqt.utils import showInfo

from ..constants import APP_NAME


class LoginWidget(QWidget):
    def __init__(self):
        super().__init__()

        # setup widget
        self.resize(300, 140)
        self.setWindowTitle(APP_NAME + " - Login")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # setup layout content
        self.email_line_edit = QLineEdit(self)
        self.password_line_edit = QLineEdit(self)
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        self.submit_push_button = QPushButton("Login")
        self.password_line_edit.returnPressed.connect(self.submit_push_button.click)

        # setup register link
        self.register_label = QLabel("<a href=\"https://www.ankisync.com/register\">New to AnkiSync? Sign up here</a>")
        self.register_label.setOpenExternalLinks(True)

        # setup forgotten password link
        self.forgotten_label = QLabel("<a href=\"https://www.ankisync.com/forgot-password\">Forgot your password?</a>")
        self.forgotten_label.setOpenExternalLinks(True)

        # setup layout
        self.layout = QFormLayout()
        self.layout.addRow(self.register_label)
        self.email_label = QLabel("Email:")
        self.layout.addRow(self.email_label, self.email_line_edit)
        self.password_label = QLabel("Password:")
        self.layout.addRow(self.password_label, self.password_line_edit)
        self.layout.addRow(self.forgotten_label)
        self.layout.addRow(self.submit_push_button)
        self.setLayout(self.layout)
        # self.adjustSize()
        self.setFixedSize(self.size())
