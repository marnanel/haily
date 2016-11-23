from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit, parse_timezone
from time import time
import email.message
import email.utils
import datetime
from haily.notes import HailyNote

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

        def currentNotes(self):
                return [HailyNote(guid=guid)
                        for guid in self.currentNoteGUIDs()]

        def currentNoteGUIDs(self):
                """
                Returns a set of strings, the GUIDs of the
                notes currently in the tree.
                """
                if MASTER not in self:
                        return set([])

                tree = self[self[MASTER].tree]
                return self._noteGUIDsInTree(tree)

        def _noteGUIDsInTree(self, tree):
                result = set()

                for item in tree.iteritems():
                        if item.path.startswith('notes/'):
                                guid = item.path[6:]
                                result.add(guid)

                return result

        def noteGUIDsSince(self, since):

                result = set()

                if not MASTER in self:
                        return result

                # The protocol counts the first commit as 1.
                # But we're starting counting from the
                # latest commit. So we have to know the
                # number of commits to convert them.
                commitsCount = self.numberOfCommits()

                theseGUIDs = thoseGUIDs = None
                commit = self[MASTER]

                # For every commit in the history,
                # "theseGUIDs" is the set of notes which
                # existed as of that commit, and
                # "thoseGUIDs" is the set of notes which
                # existed in the commit immediately after it.
                # (Since we're moving backwards through time,
                # the commit immediately after it is the
                # one we've just looked at.)
                for i in range((commitsCount-since)+1):

                        if commit is None:
                                # there's no commit, so no notes
                                theseGUIDs = set([])
                        else:
                                theseGUIDs = self._noteGUIDsInTree(self[commit.tree])

                        if thoseGUIDs is not None:

                                diff = thoseGUIDs.difference(theseGUIDs)
                                result = result.union(diff)

                        thoseGUIDs = theseGUIDs

                        if commit is None or len(commit.parents)==0:
                                # Final time round:
                                # the first commit came after
                                # an empty tree.
                                commit = None
                        else:
                                commit = self[commit.parents[0]]

                return result

        def _describeNoteOperation(self, opName, note):
                return '%10s: %-30s %36s\n' % (
                        opName,
                        note['title'][:30],
                        note['guid'],
                        )

        def _ensurePartialTree(self):
                if self._partialTree is not None:
                        # we were partway through a commit,
                        # so just pick up the tree where we left off
                        return
                elif MASTER in self:
                        # grab the tree from the master branch,
                        # if we can
                        self._partialTree = self[self[MASTER].tree]
                else:
                        # make a new tree. This can happen
                        # when there's no master ref,
                        # for example in a completely new repo.
                        self._partialTree = Tree()

        def putHailyNote(self, note,
                branch=MASTER,
                doCommit=True,
                commitMessage=None):

                filename = b'notes/'+bytes(note['guid'])
                noteBlob = Blob.from_string(bytes(note))

                self._ensurePartialTree()

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
                        self.hailyCommit()

        def hailyCommit(self):
                """
                Finishes a partial commit-- one that was started
                by passing doCommit=False to putHailyNote or
                deleteHailyNote. You can also commit by
                adding or deleting another note and
                passing doCommit=True (the default).

                If there's no partial commit in progress,
                does nothing.
                """

                if self._partialTree is None:
                        return

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

                if MASTER in self:
                        commit.parents = [self.refs[MASTER]]

                self.object_store.add_object(self._partialTree)
                self.object_store.add_object(commit)
                self.refs[MASTER] = commit.id

                self._partialTree = None
                self._commitMessage = ''

        def deleteHailyNote(self, note,
                branch=MASTER,
                doCommit=True,
                commitMessage=None):

                filename = b'notes/'+bytes(note['guid'])

                self._ensurePartialTree()

                if filename not in self._partialTree:
                        raise ValueError(note['guid']+" not found to delete")

                self._commitMessage += self._describeNoteOperation(
                        'deleted',
                        note,
                        )

                del self._partialTree[filename]

                if doCommit:
                        self.hailyCommit()

        def numberOfCommits(self):
                if not MASTER in self:
                        return 0

                result = 0
                commit = self[self.refs[MASTER]]

                while commit is not None:

                        result += 1
                        if len(commit.parents)==0:
                                break

                        # A commit could have multiple parents,
                        # but it's not clear what we should do
                        # about that. So let's just take the first one.
                        commit = self[commit.parents[0]]

                return result

        def as_dict(self):
                result = {
                        "latest-sync-revision": self.numberOfCommits(),
                        "notes": [note.as_dict() for note in self.currentNotes()],
                        }

                return result

