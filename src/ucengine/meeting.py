__author__ = "mathieu@garambrogne.net"

import urllib
import gevent

from core import Eventualy

class Meeting(Eventualy):
    "A meeting (a room)"
    def __init__(self, namei, start=0, end="never", metadata={}):
        Eventualy.__init__(self)
        self.name = name
        self.start = start
        self.end = end
        self.metadata = metadatada
        self.roster = set()
        self.twitter_hash_tags = set()
        self.callbacks = {
            'internal.roster.add': lambda event: self.roster.add(event['from']),
            #'internal.roster.delete': lambda event: self.roster.remove(
            #    event['from']),
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
        self.event_loop('/live/%s?%s' % (self.meeting, urllib.urlencode({
            'uid'   : self.user.uid,
            'sid'   : self.user.sid,
            'mode': 'longpolling'
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
