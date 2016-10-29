from haily.notes import HailyNote
from haily.repo import HailyRepo

def putnote_test():
        repo = HailyRepo('/home/marnanel/proj/hailyNotes/')
        note = HailyNote()

        repo.putNote(note)

