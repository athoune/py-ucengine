__author__ = "mathieu@garambrogne.net"

from gevent import monkey
monkey.patch_all()

import urllib

from ucengine.core import Eventualy, UCError
from ucengine.meeting import Meetings

class User(Eventualy):
    "A user"
    def __init__(self, name):
        Eventualy.__init__(self)
        self.name = name
        self.sid = None
        self.meetings = Meetings(self)
    #def __del__(self):
    #    if self.event_pid != None:
    #        self.unpresence()
    def presence(self, uce, credential):
        "I'm coming"
        self.ucengine = uce
        status, resp = self.ucengine.request('POST', '/presence/', {
            'name'               : self.name,
            'credential'         : credential,
            'metadata[nickname]' : self.name}
            )
        if status == 201:
            self.sid = resp['result']['sid']
            self.uid = resp['result']['uid']
            self.event_loop('/event?%s' % urllib.urlencode({
                'uid'   : self.uid,
                'sid'   : self.sid,
                '_async': 'lp'
                }))
        else:
            raise UCError(status, resp)
    def unpresence(self):
        "I'm leaving"
        status, resp = self.ucengine.request('DELETE',
            '/presence/%s?%s' % (self.sid, urllib.urlencode({
                'uid': self.uid,
                'sid': self.sid}))
                )
        #print resp
        if status != 200:
            raise UCError(status, resp)
        self.event_stop()
    def time(self):
        "What time is it"
        status, resp = self.ucengine.request('GET',
            '/time?%s' % urllib.urlencode({
                'uid': self.uid, 'sid': self.sid}))
        assert status == 200
        return resp['result']
    def infos(self):
        "Infos about the server"
        status, resp = self.ucengine.request('GET',
            '/infos?%s' % urllib.urlencode({
            'uid': self.uid, 'sid': self.sid}))
        assert status == 200
        return resp['result']

