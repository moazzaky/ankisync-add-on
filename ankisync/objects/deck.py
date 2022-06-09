import re
import uuid


class AnkiDeckId:
    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        if not isinstance(value, int):
            raise TypeError("AnkiId must be an integer.")

        if int(value) < 0:
            raise ValueError("AnkiId must be a positive integer.")
        self.value = int(value)


class AnkiSyncDeckId:
    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        uuid.UUID(value)  # throws any exception if not valid uuid
        self.value = value


class AnkiSyncDeckName:
    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        if not re.match(r"^[\s\w-]*$", value):
            raise ValueError("Deck name must only contain alphanumeric characters, hyphens, underscores, "
                             "and separating spaces.")
        self.value = value


class AnkiSyncDeckDescription:
    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise ValueError("Deck description must be a string")
        self.value = value


class AnkiSyncUpdatedAt:
    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        # fixme: add validation
        self.value = value


class AnkiSyncLastSyncedAt:
    def __get__(self, obj, objtype=None
                ):
        return self.value

    def __set__(self, obj, value):
        # fixme: add validation
        self.value = value


def anki_deck_id(attr):
    def decorator(cls):
        setattr(cls, attr, AnkiDeckId())
        return cls

    return decorator


def ankisync_deck_id(attr):
    def decorator(cls):
        setattr(cls, attr, AnkiSyncDeckId())
        return cls

    return decorator


def ankisync_deck_name(attr):
    def decorator(cls):
        setattr(cls, attr, AnkiSyncDeckName())
        return cls

    return decorator


def ankisync_deck_description(attr):
    def decorator(cls):
        setattr(cls, attr, AnkiSyncDeckDescription())
        return cls

    return decorator


def ankisync_updated_at(attr):
    def decorator(cls):
        setattr(cls, attr, AnkiSyncUpdatedAt())
        return cls

    return decorator


def ankisync_last_synced_at(attr):
    def decorator(cls):
        setattr(cls, attr, AnkiSyncLastSyncedAt())
        return cls

    return decorator


@anki_deck_id("anki_id")
@ankisync_deck_id("ankisync_id")
@ankisync_deck_name("name")
@ankisync_deck_description("description")
class Deck:
    def __init__(self, anki_id, ankisync_id, name, description, updated_at, last_synced_at, flashcards):
        self.anki_id = anki_id
        self.ankisync_id = ankisync_id
        self.name = name
        self.description = description
        self.updated_at = updated_at
        self.last_synced_at = last_synced_at
        self.flashcards = flashcards
