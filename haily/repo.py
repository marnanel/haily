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

        def __init__(self, *args, **kwargs):
                super(HailyRepo, self).__init__(*args, **kwargs)

                ##
                # If you ask a method not to do an automatic commit,
                # then we store the partially-updated tree here.
                self._partialTree = None

                ##
                # If you ask a method not to do an automatic commit,
                # we build the commit message here.
                self._commitMessage = ''
        
        def getHailyUser(self, username):
                pass

        def listHailyNotes(self,
                since=None,
                ):
                pass

        def _describeNoteOperation(self, opName, note):
                return '%10s: %-30s %36s\n' % (
                        opName,
                        note['title'][:30],
                        note['guid'],
                        )

        def putHailyNote(self, note,
                branch=MASTER,
                doCommit=True,
                commitMessage=None):

                filename = b'notes/'+bytes(note['guid'])
                noteBlob = Blob.from_string(bytes(note))

                if self._partialTree is not None:
                        # we were partway through a commit,
                        # so just pick up the tree where we left off
                        pass
                elif MASTER in self:
                        # grab the tree from the master branch,
                        # if we can
                        self._partialTree = self[self[MASTER].tree]
                else:
                        # make a new tree. This can happen
                        # when there's no master ref,
                        # for example in a completely new repo.
                        self._partialTree = Tree()

                if filename in self._partialTree:
                        operationName = 'changed'
                else:
                        operationName = 'added'
                self._commitMessage += self._describeNoteOperation(
                        operationName,
                        note,
                        )

                self.object_store.add_object(noteBlob)
                self._partialTree.add(filename, BASIC_PERMISSIONS, noteBlob.id)

                if doCommit:
                        self._commit()

        def _commit(self):

                if self._partialTree is None:
                        raise ValueError("attempted commit on empty tree")

                if self._commitMessage=='':
                        self._commitMessage = 'Haily checkin'

                commit = Commit()
                commit.tree = self._partialTree.id
                commit.author = commit.committer = 'Haily user <user@haily>'
                commit.encoding = 'UTF-8'
                commit.message = self._commitMessage
                commit.commit_time = commit.author_time = int(time())
                tz = parse_timezone(b'+0000')[0]
                commit.commit_timezone = commit.author_timezone = tz

                self.object_store.add_object(self._partialTree)
                self.object_store.add_object(commit)
                self.refs[MASTER] = commit.id

                self._partialTree = None
                self._commitMessage = ''

        def deleteHailyNote(self, guid):
                pass

