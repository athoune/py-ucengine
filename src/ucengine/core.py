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
