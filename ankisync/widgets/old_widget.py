# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

from aqt.qt import pyqtSignal, pyqtSlot, Qt
from aqt.qt import QWidget, QVBoxLayout, QPushButton, QProgressBar, QTextEdit

from ..config import APP_NAME


class OldWidget(QWidget):
    close_event = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # setup widget
        self.resize(300, 300)
        self.setWindowTitle(APP_NAME + ' - Sync')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # setup layout content
        self.done_button = QPushButton('Done')
        self.done_button.hide()
        self.done_button.clicked.connect(self.close)
        self.cancel_button = QPushButton('Cancel')
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat('Syncing... %p%')
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.text_edit = QTextEdit()
        self.text_edit.setDisabled(True)
        self.text_edit.setStyleSheet('background-color: rgb(255, 255, 255);')

        # setup layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.cancel_button)
        self.layout.addWidget(self.done_button)
        self.setLayout(self.layout)

    # adds text followed by new line
    # @QtCore.pyqtSlot(str)
    def append_text_edit(self, value):
        self.text_edit.append(value)
        # self.text_edit.append('\n')

    @pyqtSlot()
    def clear_text_edit(self):
        self.text_edit.clear()

    # change the progress bar value to show progress
    def set_progress_bar_value(self, progress):
        p, m = (progress)
        self.progress_bar.setValue(p)
        if m is not None:
            self.append_text_edit(m)

    def show_done_button(self):
        self.cancel_button.hide()
        self.done_button.show()


    # override closeEvent
    def closeEvent(self, event):
        self.clear_text_edit()
        self.cancel_button.show()
        self.done_button.hide()
        self.close_event.emit("Closed")
