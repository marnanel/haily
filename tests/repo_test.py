from haily.notes import HailyNote
from haily.repo import HailyRepo
from dulwich.repo import Repo
import tempfile
import nose.tools

MASTER = 'refs/heads/master'

# XXX we need a teardown routine to remove the directory

def make_test_repo():
        directory = tempfile.mkdtemp(
                prefix='hailyTest',
                )
        Repo.init_bare(path=directory)

        repo = HailyRepo(root=directory)
        return repo

def assert_notes_in_repo(repo, notes):
        tree = repo[repo[MASTER].tree]

        found = [x.path for x in tree.items() if x.path.startswith('notes/')]
        want = [b'notes/'+bytes(x['guid']) for x in notes]

        assert set(found)==set(want)

def put_notes_in_repo(repo, notes):
        for note in notes:
                repo.addNote(notes)

def putnote_test():
        repo = make_test_repo()

        note = HailyNote()
        repo.putHailyNote(note)

        assert_notes_in_repo(repo, [note])

def put_2_notes_test():
        repo = make_test_repo()

        note1 = HailyNote()
        note2 = HailyNote()
        repo.putHailyNote(note1)
        repo.putHailyNote(note2)

        assert_notes_in_repo(repo, [note1, note2])

def replace_note_test():

        repo = make_test_repo()

        note1 = HailyNote()
        repo.putHailyNote(note1)

        note2 = HailyNote(guid=note1['guid'])
        repo.putHailyNote(note2)

        assert_notes_in_repo(repo, [note2])

def split_commit_test():

        repo = make_test_repo()

        note1 = HailyNote()
        repo.putHailyNote(note1,
                doCommit=False)

        note2 = HailyNote()
        repo.putHailyNote(note2)

        assert_notes_in_repo(repo, [note1, note2])

        # ...and assert that there's only one commit
        commit = repo[repo.refs[MASTER]]
        assert len(commit.parents)==0

def delete_note_test():

        repo = make_test_repo()

        note1 = HailyNote()
        repo.putHailyNote(note1)

        note2 = HailyNote()
        repo.putHailyNote(note2)

        assert_notes_in_repo(repo, [note1, note2])

        repo.deleteHailyNote(note1)

        assert_notes_in_repo(repo, [note2])

def count_commits_test():

        repo = make_test_repo()
        assert(repo.numberOfCommits()==0)

        repo.putHailyNote(HailyNote())
        assert(repo.numberOfCommits()==1)

        repo.putHailyNote(HailyNote())
        assert(repo.numberOfCommits()==2)

def currentNotes_test():
        repo = make_test_repo()

        note1 = HailyNote()
        note2 = HailyNote()
        note1guid = str(note1['guid'])
        note2guid = str(note2['guid'])

        assert repo.currentNoteGUIDs() == set([])
        #assert repo.noteGUIDsSince(0) == set([])

        repo.putHailyNote(note1)
        assert repo.currentNoteGUIDs() == set([note1guid])
        #assert repo.noteGUIDsSince(0) == set([note1guid])

        repo.putHailyNote(note2)
        assert repo.currentNoteGUIDs() == set([note1guid, note2guid])
        assert repo.noteGUIDsSince(0) == set([note1guid, note2guid])
        assert repo.noteGUIDsSince(1) == set([note2guid])

        repo.deleteHailyNote(note1)
        assert repo.currentNoteGUIDs() == set([note2guid])
        #assert repo.noteGUIDsSince(0) == set([note1guid])

def as_dict_test():

        def clear_dates(d):
                for n in d['notes']:
                        for k in n.keys():
                                if k.endswith('-date'):
                                        n[k] = '(date)'

        def sort_notes(d):
                # We need this because "notes" is essentially a set,
                # but you can't have a set of dictionaries.
                # So we need to sort the list to enable comparison.
                d['notes'] = sorted(d['notes'])

        def compare(received, expected):
                clear_dates(received)
                sort_notes(received)
                sort_notes(expected)
                nose.tools.assert_dict_equal(received, expected)

        repo = make_test_repo()

        note1 = HailyNote()
        note2 = HailyNote()
        note1guid = str(note1['guid'])
        note2guid = str(note2['guid'])

        compare(repo.as_dict(),
                        {'notes': [], 'latest-sync-revision': 0})

        repo.putHailyNote(note1)

        compare(repo.as_dict(),
                        {'notes': [
                                {'note-content': 'Describe your note here.',
                                'open-on-startup': 'False',
                                'last-metadata-change-date': '(date)',
                                'title': 'New note',
                                'tags': [],
                                'create-date': '(date)',
                                'pinned': 'False',
                                'note-content-version': '0.1',
                                'last-change-date': '(date)',
                                'guid': note1guid,
                                },
                                ],
                        'latest-sync-revision': 1})

        repo.putHailyNote(note2)
        compare(repo.as_dict(),
                        {'notes': [
                                {'note-content': 'Describe your note here.',
                                'open-on-startup': 'False',
                                'last-metadata-change-date': '(date)',
                                'title': 'New note',
                                'tags': [],
                                'create-date': '(date)',
                                'pinned': 'False',
                                'note-content-version': '0.1',
                                'last-change-date': '(date)',
                                'guid': note1guid,
                                },
                                {'note-content': 'Describe your note here.',
                                'open-on-startup': 'False',
                                'last-metadata-change-date': '(date)',
                                'title': 'New note',
                                'tags': [],
                                'create-date': '(date)',
                                'pinned': 'False',
                                'note-content-version': '0.1',
                                'last-change-date': '(date)',
                                'guid': note2guid,
                                },
                                ],
                                'latest-sync-revision': 2})

        repo.deleteHailyNote(note1)
        compare(repo.as_dict(),
                        {'notes': [
                                {'note-content': 'Describe your note here.',
                                'open-on-startup': 'False',
                                'last-metadata-change-date': '(date)',
                                'title': 'New note',
                                'tags': [],
                                'create-date': '(date)',
                                'pinned': 'False',
                                'note-content-version': '0.1',
                                'last-change-date': '(date)',
                                'guid': note2guid,
                                },
                                ],
                                'latest-sync-revision': 3})

