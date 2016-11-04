import git
import email.message
import email.utils
import time
import datetime
from uuid import uuid4
import json

class HailyNote(object):

        def __init__(self,
                source=None,
                uuid=None):

                now = datetime.datetime.now()

                if uuid is None:
                        uuid = uuid4()

                self._content = {
                                'title': 'New note',
                                'note-content': 'Describe your note here.',
                                'note-content-version': '0.1',
                                'last-change-date': now,
                                'last-metadata-change-date': now,
                                'create-date': now,
                                'open-on-startup': False,
                                'pinned': False,
                                'tags': [],
                                'uuid': uuid,
                }

                if source is not None:
                        message = email.message_from_string(source)

                        for (field, value) in message.items():

                                if field=='tag':
                                        # special-cased; ignore
                                        continue

                                self[field] = value

                        self._content['tags'] = message.get_all('tag', [])

                        if not message.is_multipart():
                                self._content['note-content'] = message.get_payload()
                        else:
                                # should never happen
                                raise ValueError('message was multipart')
 
        def __str__(self):
                message = email.message.Message()

                # Strings and booleans
                for field in ('title', 'note-content-version',
                        'open-on-startup', 'pinned'):

                        message.add_header(field,
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

                        message.add_header(field, str(value))

                # Tags
                for tag in self._content['tags']:
                        message.add_header('tag', tag)

                # note-content, stored as the payload (body) of the message
                message.set_payload(self._content['note-content'])

                return message.as_string()

        def __getitem__(self, field):
                return self.getItem(field,
                        as_string=False)

        def __setitem__(self, field, value):
                return self.setItem(field, value)

        def getItem(self, field, as_string=False):
                value = self._content[field]

                if as_string:
                        if type(value)==datetime.datetime:
                                return value.isoformat()
                        else:
                                return str(value)
                else:
                        return value

        def setItem(self, field, value):

                # XXX at some point this should have a parameter
                # to specify whether to update the metadata change time too

                if value is None:
                        raise ValueError('value was None')

                if field in (
                                # Strings
                                'title',
                                'note-content',
                                'note-content-version',
                                ):
                        self._content[field] = str(value)

                elif field in (
                                # Dates
                                'last-change-date',
                                'last-metadata-change-date',
                                'create-date',
                 ):
                        if type(value)==str:
                                value = email.utils.parsedate(value)
                                
                                if value is None:
                                        raise ValueError('string didn\'t represent a date')

                                self._content[field] = value

                        elif type(value)==datetime.datetime:
                                self._content[field] = value
                        else:
                                raise ValueError('we need a string or a datetime')

                elif field in (
                                # Booleans
                               'open-on-startup',
                               'pinned',
                ):
                        if type(value)==str:
                                self._content[field] = (value.lower()=='true')
                        elif type(value)==bool:
                                self._content[field] = value
                        else:
                                raise ValueError('we need a string or a bool')

                elif field in (
                                # Lists
                                'tags',
                ):
                        if type(value)==list:
                                self._content[field] = value
                        else:
                                raise ValueError('we need a list')

                elif field=='uuid':
                        raise KeyError('uuid must be set in the constructor')

                else:
                        raise KeyError(field)

        def as_json(self):

                obj = {}

                for field in (
                        'title', 'note-content', 'note-content-version',
                        'last-change-date', 'last-metadata-change-date',
                        'create-date',
                        'open-on-startup', 'pinned',
                        'uuid',
                        ):
                        obj[field] = self.getItem(field, as_string=True)

                obj['tags'] = self['tags']

                return json.dumps(obj, sort_keys=True, indent=8)
