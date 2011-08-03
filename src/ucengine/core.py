__author__ = "mathieu@garambrogne.net"

from gevent import monkey
import gevent

monkey.patch_all()

#FIXME one error per HTTP error : 400, 401, 404, 500
class UCError(Exception):
    "Standard error coming from the server"

    def __init__(self, code, value):
        Exception.__init__(self)
        self.code = code
        self.value = value

    def __repr__(self):
        return "<UCError:%i %s>" % (self.code, self.value)

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

def unicode_urlencode(params):
    clean = {}
    for k, v in params.items():
        if isinstance(v, unicode):
            clean[k] = v.encode('utf-8')
        else:
            clean[k] = v
    return clean
 
