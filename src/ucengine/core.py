__author__ = "mathieu@garambrogne.net"

import json

from gevent import monkey
import gevent

monkey.patch_all()

import httplib
import urllib

class UCError(Exception):
    "Standard error coming from the server"
    def __init__(self, code, value):
        Exception.__init__(self)
        self.code = code
        self.value = value
    def __repr__(self):
        return "<UCError:%i %s>" % (self.code, self.value)

class UCEngine(object):
    "The Server"
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.users = []
    def request(self, method, path, body=None):
        "ask something to the server"
        connection = httplib.HTTPConnection(self.host, self.port)
        if body != None:
            connection.request(method, '/api/0.6%s' % path,
                urllib.urlencode(body))
        else:
            connection.request(method, '/api/0.6%s' % path)
        resp = connection.getresponse()
        raw = resp.read()
        response = json.loads(raw)
        connection.close()
        return resp.status, response
    def connect(self, user, credential):
        status, resp = self.request('POST', '/presence/', {
            'name'               : user.name,
            'credential'         : credential,
            'metadata[nickname]' : user.name}
            )
        if status == 201:
            return Session(self, resp['result']['uid'], resp['result']['sid'])
        else:
            raise UCError(status, resp)

class Eventualy(object):
    "Dummy object implementing event loop"
    def __init__(self):
        self.callbacks = {}
        self.event_pid = None
        self.ucengine = None
    def callback(self, key, cback):
        "register a new callback"
        self.callbacks[key] = cback
        return self
    def event_loop(self, url):
        "launch the backround event listening"
        def _listen():
            start = 0
            while True:
                status, resp = self.ucengine.request('GET',
                    "%s&start=%i" % (url, start))
                if status == 200:
                    for event in resp['result']:
                        start = event['datetime'] + 1
                        if event['type'] in self.callbacks:
                            gevent.spawn(self.callbacks[event['type']], event)
                        else:
                            pass
                            #print event['type'], event
        self.event_pid = gevent.spawn(_listen)
    def event_stop(self):
        "stop the event loop"
        self.event_pid.kill()

class Session(Eventualy):
    def __init__(self, uce, uid, sid):
        Eventualy.__init__(self)
        self.ucengine = uce
        self.uid = uid
        self.sid = sid
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
    def loop(self):
        self.event_loop('/live?%s' % urllib.urlencode({
                'uid'   : self.uid,
                'sid'   : self.sid,
                'mode': 'longpolling'
                }))
        return self
    def close(self):
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
 
