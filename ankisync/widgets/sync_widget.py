# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

import sys

# import from anki's custom qt import :-)
from aqt import mw
from aqt.operations import QueryOp
from aqt.qt import (
    pyqtSignal,
    Qt,
    QApplication,
    QDesktopServices,
    QFont,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPainterPath,
    QProgressBar,
    QPushButton,
    QRectF,
    QRegion,
    QTableWidget,
    QTextCursor,
    QTextEdit,
    QThreadPool,
    QUrl,
    QVBoxLayout,
    QWidget,
)
from aqt.utils import showInfo

from .decks_widget import DecksWidget
from .. import api
from ..sync import Sync
from ..constants import APP_NAME
from ..message_boxes.confirmation_message_box import ConfirmationMessageBox
from ..utils import access_token
from ..worker import Worker

# todo: is a cancel button necessary


class SyncWidget(QWidget):
    close_event = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # self.setWindowIcon()

        # setup widget
        # self.resize(800, 700)
        self.setWindowTitle(APP_NAME + ': Collaborative Decks Made Easy')
        # self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # description bar layout
        title = QLabel()
        title.setText("Sync Your Decks with AnkiSync Servers")
        title.setFont(QFont('Arial', 15))
        title.setStyleSheet("font-weight: 700")
        version = QLabel()
        version.setText("AnkiSync \n v1.0.0")
        version.setStyleSheet("font-style: italic")
        description_bar_layout = QHBoxLayout()
        description_bar_layout.addWidget(title)
        description_bar_layout.addStretch()
        description_bar_layout.addWidget(version)

        # horizontal separator
        horizontal_separator = QFrame()
        horizontal_separator.setFrameShape(QFrame.HLine)
        horizontal_separator.setFrameShadow(QFrame.Sunken)
        horizontal_separator.setLineWidth(1)

        # button bar, aka links for visit website, help, logout
        self.button_bar = QHBoxLayout()
        website_button = QPushButton()
        website_button.setFixedSize(125, 25)
        website_button.setText("Visit AnkiSync Website")
        website_button.clicked.connect(website_button_clicked)
        find_decks_button = QPushButton()
        find_decks_button.setFixedSize(75, 25)
        find_decks_button.setText("Find Decks")
        find_decks_button.clicked.connect(find_decks_button_clicked)
        help_button = QPushButton()
        help_button.setFixedSize(55, 25)
        help_button.setText("Get Help")
        help_button.clicked.connect(help_button_clicked)
        logout_button = QPushButton()
        logout_button.setText("Log Out")
        logout_button.setFixedSize(55, 25)
        logout_button.clicked.connect(self.logout_button_clicked)
        self.button_bar.addWidget(find_decks_button)
        self.button_bar.addWidget(website_button)
        self.button_bar.addWidget(help_button)
        self.button_bar.addStretch()
        self.button_bar.addWidget(logout_button)

        # decks groupbox with internal table widget
        self.decks_group_box = QGroupBox("Decks")
        self.decks_group_box_layout = QVBoxLayout()
        self.decks_table = DecksWidget()
        self.decks_group_box_layout.addWidget(self.decks_table)
        self.decks_group_box.setLayout(self.decks_group_box_layout)

        # text edit
        self.text_edit_group_box = QGroupBox("Status")
        self.text_edit_group_box_layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet('background-color: rgb(255, 255, 255);')
        self.text_edit_group_box_layout.addWidget(self.text_edit)
        self.text_edit_group_box.setLayout(self.text_edit_group_box_layout)

        # content
        self.content_layout = QHBoxLayout()
        self.content_layout.addWidget(self.decks_group_box)
        self.content_layout.addWidget(self.text_edit_group_box)

        # progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat('Syncing... 0%')
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # buttons
        self.done_button = QPushButton('Done')
        self.done_button.hide()
        self.done_button.clicked.connect(self.done_button_clicked)

        self.sync_button = QPushButton()
        self.sync_button.setText("Sync Decks")
        self.sync_button.clicked.connect(self.sync_button_clicked)

        # above the sync button
        self.horizontal_content = QHBoxLayout()

        # setup entire layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(description_bar_layout)
        self.layout.addWidget(horizontal_separator)
        self.layout.addLayout(self.button_bar)
        self.layout.addLayout(self.content_layout)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.sync_button)
        self.layout.addWidget(self.done_button)
        self.layout.addStretch()
        self.setLayout(self.layout)

        # set window size
        self.setFixedSize(self.layout.sizeHint())
        self.setMinimumSize(1000, 300)

    # override closeEvent
    def closeEvent(self, event):
        # self.clear_text_edit()
        # self.cancel_button.show()
        # self.done_button.hide()
        self.close_event.emit("Closed")


    def showEvent(self, event):

        return QWidget.showEvent(self, event)

    def set_remote_decks(self, subscribed_decks):

        decks = []

        for subscribed_deck in subscribed_decks:
            deck = {'name': subscribed_deck["name"]}
            decks.append(deck)

        self.decks_table.update_decks(decks)



    def set_progress_bar_percentage(self, percentage):
        self.progress_bar.setFormat(f'Syncing... {percentage}%')
        self.progress_bar.setValue(percentage)

    def done_button_clicked(self):
        self.done_button.hide()
        self.sync_button.show()
        self.progress_bar.hide()
        self.set_progress_bar_percentage(0)

    def sync_button_clicked(self):
        self.clear_text_edit()
        self.set_progress_bar_percentage(0)
        self.sync_button.hide()
        self.progress_bar.show()

        sync = Sync(self)

        # actions.py
        sync_worker = Worker(sync.run)  # Any other args, kwargs are passed to the run function
        sync_worker.signals.progress.connect(self.sync_signal_progress)
        # sync worker

        sync_worker.signals.finished.connect(self.sync_signal_finished)

        QThreadPool.globalInstance().start(sync_worker)

        mw.taskman.run_on_main(lambda: mw.deckBrowser.refresh())

    def sync_signal_progress(self, progress):
        (text, percentage) = progress
        self.set_progress_bar_percentage(percentage)

        if text is not None:
            self.append_text_edit(text)

    def sync_signal_finished(self):
        self.done_button.show()

    def append_text_edit(self, text):
        # insert at home
        # set the cursor position to 0
        #cursor = QTextCursor(self.text_edit.document())
        # set the cursor position (defaults to 0 so this is redundant)
        #cursor.setPosition(0)
        #self.text_edit.setTextCursor(cursor)

        #self.text_edit.insertPlainText(text)
        #self.text_edit.insertPlainText('\n')

        # append allows for HTML styling
        self.text_edit.append(text)
        # self.text_edit.append('\n')

    def clear_text_edit(self):
        self.text_edit.clear()

    def logout_button_clicked(self):
        # confirm button -> delete token, reset sync widget, close sync widget
        confirm = ConfirmationMessageBox("Are you sure you want to log out?",
                                         "We are sad to see you go. Hopefully you are just switching "
                                         "accounts! Thank you for using AnkiSync, we appreciate you. <3")
        if confirm.response == QMessageBox.Yes:
            result = access_token.delete()
            self.hide()


def find_decks_button_clicked():
    QDesktopServices.openUrl(QUrl("https://www.ankisync.com/decks"))


def help_button_clicked():
    QDesktopServices.openUrl(QUrl("https://www.ankisync.com/help"))





def website_button_clicked():
    QDesktopServices.openUrl(QUrl("https://www.ankisync.com"))
