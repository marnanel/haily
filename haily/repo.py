from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit, parse_timezone
from time import time
import email.message
import email.utils
import datetime

BASIC_PERMISSIONS = 0o100644

class HailyRepo(object):
        """
        This class doesn't handle authentication.

        We don't provide a way to retrieve a particular
        note; the spec says this isn't required for sync,
        which is good because it's not obvious which note
        the ID number given should refer to.
        """
        
        def __init__(self, path, username='user'):
                self._git = Repo(path)
                self._username = username

        def getUser(self, username):
                pass

        def listNotes(self,
                since=None,
                ):
                pass

        def putNote(self, note):
                print 'got note:', note

                noteBlob = Blob.from_string(str(note))

                tree = Tree()
                tree.add(b'test', BASIC_PERMISSIONS, noteBlob.id)

                commit = Commit()
                commit.tree = tree.id
                commit.author = commit.committer = 'Thomas Thurman <thomas@thurman.org.uk>'
                commit.encoding = 'UTF-8'
                commit.message = 'Hello world'

                commit.commit_time = commit.author_time = int(time())
                tz = parse_timezone(b'-0200')[0]
                commit.commit_timezone = commit.author_timezone = tz

                store = self._git.object_store
                store.add_object(noteBlob)
                store.add_object(tree)
                store.add_object(commit)

                self._git.refs['refs/heads/master'] = commit.id

        def deleteNote(self, guid):
                pass

