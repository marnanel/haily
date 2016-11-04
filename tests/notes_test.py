from haily.notes import HailyNote
import re
import nose.tools
import json
from uuid import uuid4

I_LIKE_CATS = """title: Cats
note-content-version: 0.1
open-on-startup: False
pinned: True
tag: cats
tag: animals
tag: things I like

I like cats."""

def _remove_dates(s):
        """Replace all characters between "Date:" and
        the end of that line, in a multiline string,
        with the string "(date)"."""

        return re.sub(
                pattern=r'(date:).*$',
                repl=r'\1(date)',
                string=s,
                flags=re.IGNORECASE|re.MULTILINE)

def create_test():
        note = HailyNote()

def create_defaults_test():
        EXPECT = """title: New note
note-content-version: 0.1
open-on-startup: False
pinned: False
last-change-date:(date)
last-metadata-change-date:(date)
create-date:(date)

Describe your note here."""

        note = HailyNote()
        nose.tools.eq_(_remove_dates(str(note)), EXPECT)

def create_from_string_test():
        EXPECT = """title: Cats
note-content-version: 0.1
open-on-startup: False
pinned: True
last-change-date:(date)
last-metadata-change-date:(date)
create-date:(date)
tag: cats
tag: animals
tag: things I like

I like cats."""

        note = HailyNote(I_LIKE_CATS)
        nose.tools.eq_(_remove_dates(str(note)), EXPECT)

def create_without_uuid_test():
        note1 = HailyNote()
        note2 = HailyNote()

        note1uuid = note1['uuid']
        note2uuid = note2['uuid']

        if note1uuid is None or note2uuid is None:
                raise AssertionError('uuids are None')

        nose.tools.assert_not_equal(
                note1uuid,
                note2uuid)

def create_with_uuid_test():
        uuid = uuid4()
        note = HailyNote(uuid=uuid)
        nose.tools.eq_(
                note['uuid'],
                uuid)

def as_json_test():
        note = HailyNote()
        obj = json.loads(note.as_json())
        
        EXPECT = {
                "note-content": "Describe your note here.", 
                "note-content-version": "0.1", 
                "open-on-startup": "False", 
                "pinned": "False", 
                "tags": [], 
                "title": "New note", 
        }

        for (key, value) in EXPECT.items():
                assert obj[key]==value

