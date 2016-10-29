from haily.notes import HailyNote
import re
import nose.tools

I_LIKE_CATS = """Title: Cats
Note-Content-Version: 0.1
Open-On-Startup: False
Pinned: True
Tag: cats
Tag: animals
Tag: things I like

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
        EXPECT = """Title: New note
Note-Content-Version: 0.1
Open-On-Startup: False
Pinned: False
Last-Change-Date:(date)
Last-Metadata-Change-Date:(date)
Create-Date:(date)

Describe your note here."""

        note = HailyNote()
        nose.tools.eq_(_remove_dates(str(note)), EXPECT)

def create_from_string_test():
        EXPECT = """Title: Cats
Note-Content-Version: 0.1
Open-On-Startup: False
Pinned: True
Last-Change-Date:(date)
Last-Metadata-Change-Date:(date)
Create-Date:(date)
Tag: cats
Tag: animals
Tag: things I like

I like cats."""

        note = HailyNote(I_LIKE_CATS)
        nose.tools.eq_(_remove_dates(str(note)), EXPECT)

