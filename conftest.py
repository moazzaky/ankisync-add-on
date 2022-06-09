import pytest
from tools.anki_testing import get_anki_app

# fixme: cannot get this to work for some reason
@pytest.fixture(scope="module")
def anki():
    return get_anki_app()
    #with anki_running() as app:
        #yield app.exec()
