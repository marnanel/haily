import git
import email.message
import email.utils
import datetime

class HailyNote(object):

        def __init__(self, source=None):

                self._content = {
                                # XXX title should probably be made unique
                                'title': 'New note',
                                'note-content': 'Describe your note here.',
                                'note-content-version': '0.1',
                                'last-change-date': None,
                                'last-metadata-change-date': None,
                                'create-date': None,
                                'open-on-startup': False,
                                'pinned': False,
                                'tags': [],
                }

                if source is not None:
                        message = email.message_from_string(source)

                        for field in ('title', 'note-content-version'):
                                self._content[field] = message[field.title()]

                        for field in ('open-on-startup', 'pinned'):
                                self._content[field] = (message[field.title()]=='True')

                        # XXX dates

                        # tags
                        self._content['tags'] = message.get_all('Tag', [])

                        if not message.is_multipart():
                                self._content['note-content'] = message.get_payload()
                        # never mind if it *is* multipart;
                        # it never should be, so we can stick
                        # with the default.
 
        def __str__(self):
                message = email.message.Message()

                # Strings and booleans
                for field in ('title', 'note-content-version',
                        'open-on-startup', 'pinned'):
                        message.add_header(field.title(),
                                str(self._content[field]))

                # Dates
                for field in (
                                'last-change-date',
                                'last-metadata-change-date',
                                'create-date',
                                ):
                        value = self._content[field]
                        if value is None:
                                value = datetime.datetime.now()

                        message.add_header(field.title(), str(value))

                # Tags
                for tag in self._content['tags']:
                        message.add_header('Tag', tag)

                # note-content, stored as the payload (body) of the message
                message.set_payload(self._content['note-content'])

                return message.as_string()


