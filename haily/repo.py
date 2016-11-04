from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit, parse_timezone
from time import time
import email.message
import email.utils
import datetime

BASIC_PERMISSIONS = 0o100644
MASTER = 'refs/heads/master'

class HailyRepo(Repo):
        """
        This class doesn't handle authentication.

        We don't provide a way to retrieve a particular
        note; the spec says this isn't required for sync,
        which is good because it's not obvious which note
        the ID number given should refer to.
        """
        
        def getHailyUser(self, username):
                pass

        def listHailyNotes(self,
                since=None,
                ):
                pass

        def putHailyNote(self, note,
                branch=MASTER):

                filename = b'notes/'+bytes(note['uuid'])
                noteBlob = Blob.from_string(bytes(note))

                if MASTER in self:
                        tree = self[self[MASTER].tree]
                else:
                        tree = Tree()

                tree.add(filename, BASIC_PERMISSIONS, noteBlob.id)

                # XXX use sensible defaults here
                commit = Commit()
                commit.tree = tree.id
                commit.author = commit.committer = 'Thomas Thurman <thomas@thurman.org.uk>'
                commit.encoding = 'UTF-8'
                commit.message = 'Hello world'

                commit.commit_time = commit.author_time = int(time())
                tz = parse_timezone(b'-0200')[0]
                commit.commit_timezone = commit.author_timezone = tz

                store = self.object_store
                store.add_object(noteBlob)
                store.add_object(tree)
                store.add_object(commit)

                self.refs[MASTER] = commit.id

        def deleteHailyNote(self, guid):
                pass

