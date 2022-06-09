# This code is taken from https://github.com/searene/Anki-Addons
#https://github.com/AwesomeTTS/awesometts-anki-addon/blob/f7a724fb6ac6d66ecb219a1845d7aebb062a23ef/tools/anki_testing.py
# coding: utf-8

import tempfile
from contextlib import contextmanager

import sys

# sys.path.insert(0, 'anki_root')

import aqt
from aqt import _run
from aqt import AnkiApp
from aqt.main import AnkiQt
from aqt.profiles import ProfileManager


origin_sys_excepthook = sys.excepthook


def temporary_user(dir_name, name="__Temporary Test User__", lang="en_US"):

    # prevent popping up language selection dialog
    original = ProfileManager.setDefaultLang

    def set_default_lang(profileManager):
        profileManager.setLang(lang)

    ProfileManager.setDefaultLang = set_default_lang

    pm = ProfileManager(base=dir_name)

    pm.setupMeta()

    # create profile no matter what (since we are starting in a unique temp directory)
    pm.create(name)

    # this needs to be called explicitly
    pm.setDefaultLang()

    pm.name = name


    # cleanup move this
    #pm.remove(name)
    #ProfileManager.setDefaultLang = original


def temporary_dir():
    # create a true unique temporary directory at every startup
    tempdir = tempfile.TemporaryDirectory(suffix='anki')
    #yield tempdir.name
    # tempdir.cleanup() movie this
    return tempdir.name


def get_anki_app():

    # don't use the second instance mechanism, start a new instance every time
    def mock_secondInstance(ankiApp):
        return False

    AnkiApp.secondInstance = mock_secondInstance

    # prevent auto-updater code from running (it makes http requests)
    def mock_setupAutoUpdate(AnkiQt):
        pass

    AnkiQt.setupAutoUpdate = mock_setupAutoUpdate

    dir_name = temporary_dir()

    user_name = temporary_user(dir_name)

    argv= ["anki", "-p", user_name, "-b", dir_name]
    app = _run(argv=argv, exec=False)

    # Anki sets its own error handler, which will prevent us from
    # obtaining error messages, unload it to use the original one
    aqt.mw.errorHandler.unload()

    return app

    #app.exec()


def destroy_anki_app():

    # clean up what was spoiled
    aqt.mw.cleanupAndExit()

    # Anki sets sys.excepthook to None in cleanUpAndExit(),
    # which causes the next test to throw exceptions,
    # let's set it back
    sys.excepthook = origin_sys_excepthook

    # remove hooks added during app initialization
    from anki import hooks
    hooks._hooks = {}

    # test_nextIvl will fail on some systems if the locales are not restored
    import locale
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())

