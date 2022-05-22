# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

from aqt.qt import (
    Qt,
    QPainter,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton
)
from aqt.utils import showInfo


class DecksWidget(QTableWidget):

    def __init__(self, *args):
        QTableWidget.__init__(self, *args)

        self.decks = []

        header = self.verticalHeader()
        header.setVisible(False)

        # Row count
        self.setRowCount(0)

        # Column count
        self.setColumnCount(3)

        # Disable Editing
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)

        # self.setItem(1, 0, QTableWidgetItem("Aloysius"))
        # self.setItem(1, 1, QTableWidgetItem("Indore"))
        # self.setItem(2, 0, QTableWidgetItem("Alan"))
        # self.setItem(2, 1, QTableWidgetItem("Bhopal"))
        # self.setItem(3, 0, QTableWidgetItem("Arnavi"))
        # self.setItem(3, 1, QTableWidgetItem("Mandsaur"))

        # self.setCellWidget(0,0, QPushButton("Test"))
        # self.setCellWidget(1,1, QPushButton("Test"))

        # Table will fit the screen horizontally
        # self.horizontalHeader().setStretchLastSection(True)
        # self.horizontalHeader().setSectionResizeMode(
        # QHeaderView.Stretch)

        # set headers
        self.setHorizontalHeaderItem(0, QTableWidgetItem('Deck Name'))
        self.setHorizontalHeaderItem(1, QTableWidgetItem('Full Sync'))
        self.setHorizontalHeaderItem(2, QTableWidgetItem('Errors'))

        # self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().resizeSection(1, 70)
        self.horizontalHeader().resizeSection(2, 50)

    def update_decks(self, decks):

        self.decks = decks

        rows = len(decks)

        self.setRowCount(rows)

        for index, deck in enumerate(decks):
            if "name" in deck:
                self.setItem(index, 0, QTableWidgetItem(deck["name"]))
                self.setItem(index, 1, QTableWidgetItem(""))
                self.setItem(index, 2, QTableWidgetItem(""))

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.model() is not None and self.model().rowCount() > 0:
            return
        painter = QPainter(self.viewport())
        painter.save()
        col = self.palette().placeholderText().color()
        painter.setPen(col)
        fm = self.fontMetrics()
        elided_text = fm.elidedText(
            'Hit the "sync decks" button below to get started. :-)', Qt.ElideRight, self.viewport().width()
        )
        painter.drawText(self.viewport().rect(), Qt.AlignCenter, elided_text)
        painter.restore()
