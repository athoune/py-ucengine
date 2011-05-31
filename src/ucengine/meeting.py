__author__ = "mathieu@garambrogne.net"

from ucengine.core import Eventualy

from gevent import monkey
import gevent

monkey.patch_all()

import urllib

class Meetings(object):
    "Lazy dictionnary for handling meetings"
    def __init__(self, user):
        self.meetings = {}
        self.user = user
    def __getitem__(self, meeting):
        if not meeting in self.meetings:
            self.meetings[meeting] = Meeting(meeting)
            self.meetings[meeting].ucengine = self.user.ucengine
            self.meetings[meeting].user = self.user
        return self.meetings[meeting]

class Meeting(Eventualy):
    "A meeting (a room)"
    def __init__(self, meeting):
        Eventualy.__init__(self)
        self.user = None
        self.meeting = meeting
        self.roster = set()
        self.twitter_hash_tags = set()
        self.callbacks = {
            'internal.roster.add': lambda event: self.roster.add(event['from']),
            'internal.roster.delete': lambda event: self.roster.remove(
                event['from']),
            'twitter.hashtag.add': lambda event: self.twitter_hash_tags.add(
                event['metadata']['hashtag'])
        }
    def join(self):
        "Joining the meeting"
        status, resp = self.ucengine.request('POST',
            '/meeting/all/%s/roster/' % self.meeting, {
                'uid': self.user.uid,
                'sid': self.user.sid
        })
        assert status == 200
        self.event_loop('/event/%s?%s' % (self.meeting, urllib.urlencode({
            'uid'   : self.user.uid,
            'sid'   : self.user.sid,
            '_async': 'lp'
        })))
        return self
    def chat(self, text, lang='en'):
        "Talking to the meeting"
        status, resp = self.ucengine.request('POST',
            '/event/%s' % self.meeting, {
                'uid'           : self.user.uid,
                'sid'           : self.user.sid,
                'type'          : 'chat.message.new',
                'metadata[lang]': lang,
                'metadata[text]': text
            })
        assert status == 201
        return resp['result']
    def async_chat(self, text, lang='en'):
        gevent.spawn(self.chat, text, lang)
        return self
