# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

"""
GUI.py initiates all buttons, dialog boxes, hooks, and monkey patches.
"""


from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.utils import showInfo
from . import actions
from .widgets.debug_widget import DebugWidget
from .widgets.login_widget import LoginWidget
from .widgets.sync_widget import SyncWidget
from .worker.worker import Worker
from . import utils

# todo: add teardown of hooks?


class Gui:
    # initialize GUI
    def __init__(self):
        self.setup_gui_hooks()

        # setup widgets
        self.debug_widget = DebugWidget()
        self.login_widget = LoginWidget()
        self.sync_widget = SyncWidget()

        # setup actions
        self.login_widget.submit_push_button.clicked.connect(self.start_login_worker)

        # add menu item to trigger sync
        # action = QAction("AnkiSync", mw)
        # action.triggered.connect(self.clicked_ankisync_sync_button)
        # mw.form.menuTools.addAction(action)

        # self.sync_widget.close_event.connect(showInfo)  # cancel event sent to thread
        # self.sync_widget.cancel_button.clicked.connect(self.sync_worker.signals.finished)

    def setup_gui_hooks(self):
        # sidebar hook to remove AnkiSync decks to disable editing
        # gui_hooks.browser_will_build_tree.append(browser_will_build_tree)

        # add toolbar button via gui_hooks

        # modify deck browser via gui_hooks
        gui_hooks.deck_browser_will_render_content.append(self.deck_browser_will_render_content)
        gui_hooks.overview_will_render_content.append(self.on_overview_will_render_content)
        gui_hooks.reviewer_will_show_context_menu.append(self.reviewer_will_show_context_menu)
        gui_hooks.top_toolbar_did_init_links.append(self.show_toolbar_ankisync_sync_button)

        # modify deck options via gui_hooks
        # gui_hooks.deck_conf_did_setup_ui_form.append(self.deck_conf_did_setup_ui_form)
        # gui_hooks.deck_browser_will_show_options_menu.append(self.deck_browser_will_show_options_menu)

    def reviewer_will_show_context_menu(self, reviewer, menu):
        showInfo(reviewer.card)

    # this will show during the "deck preview page"
    def on_overview_will_render_content(self, overview, content):
        test = "test"
        # content.table += "\n<div>my html</div>"

    def deck_conf_did_setup_ui_form(self, deck_conf):
        # deck_conf.form.desc.setReadOnly(True)
        todo = "todo"

    def progress_fn(self, progress):
        p, m = (progress)
        showInfo("%d%% done %s" % (p, m))

    # this will show during the main "decks preview page"
    def deck_browser_will_render_content(self, deck_browser, content):
        content.stats += "\n<div>Note: Do not rename or delete AnkiSync decks locally.</div>"

    def deck_browser_will_show_options_menu(self, menu, deck_id):
        menu.clear()

    def editor_will_load_note(self):
        return

    def clicked_ankisync_sync_button(self):

        if utils.access_token.get() is not None:

            if self.sync_widget.isVisible():
                self.sync_widget.raise_()
                self.sync_widget.activateWindow()
            else:
                self.sync_widget.show()
            # actions.py
            #sync_worker = Worker(actions.start_sync)  # Any other args, kwargs are passed to the run function
            #sync_worker.signals.progress.connect(self.sync_widget.set_progress_bar_value)
            # sync worker

            # sync_worker.signals.progress()
            #sync_worker.signals.finished.connect(self.sync_widget.show_done_button)

            #QThreadPool.globalInstance().start(sync_worker)
        else:
            self.login_widget.show()
        # commands.start_sync()

        # Execute worker for syncing
        # QThreadPool.globalInstance().start(worker)
        # Pass the function to execute

        # worker.signals.result.connect(self.print_output)

        # worker.signals.progress.connect(self.progress_fn)

    def show_toolbar_ankisync_sync_button(self, links, toolbar):

        links.append(
            toolbar.create_link(
                "sync-with-ankisync", "AnkiSync", self.clicked_ankisync_sync_button,
                tip="Updates decks with AnkiSync", id="sync-with-ankisync"
            )
        )

    # login worker
    def start_login_worker(self):
        login_worker = Worker(actions.login, self.login_widget.email_line_edit.text(), self.login_widget.password_line_edit.text())  # Any other args, kwargs are passed to the run function
        login_worker.signals.result.connect(self.result_login_worker)
        login_worker.signals.error.connect(self.error_login_worker)
        login_worker.signals.finished.connect(self.finished_login_worker)
        QThreadPool.globalInstance().start(login_worker)

    def finished_login_worker(self):
        if utils.access_token.get() is not None:
            self.login_widget.hide()

    def result_login_worker(self, result):
        if result['success'] is False:
            showInfo(result['message'])
        else:
            utils.access_token.set(result['access_token'])
            showInfo("You have successfully logged in! :)")
            # self.sync_widget

    def error_login_worker(self, results):
        showInfo(str(results))

    # sync worker


# avoid garbage collection, https://addon-docs.ankiweb.net/qt.html, todo: is this right?


