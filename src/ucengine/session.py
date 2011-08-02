import urllib

from core import Eventualy, unicode_urlencode
from user import User
from meeting import Meeting

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
    def save(self, data):
        if issubclass(data.__class__, User):
            self._save_user(data)
        if issubclass(data.__class__, Meeting):
            self._save_meeting(data)
    def _save_meeting(self, data):
        values = {
            'start': data.start,
            'end': data.end,
            'metadata': data.metadata,
            'uid': self.uid,
            'sid': self.sid,
         }
        status, resp = self.ucengine.request('GET',
            '/meeting/all/%s?%s' % (data.name),
            urllib.urlencode({'uid':self.uid, 'sid': self.sid}))
        if status == 200:
            status, resp = self.ucengine.request('PUT',
            '/meeting/all/%s' % data.name,
            unicode_urlencode(values))
            assert status == 200
        else:
            status, resp = self.ucengine.request('POST',
            '/meeting/all/',
            unicode_urlencode(values))
            assert status == 201
    def _save_user(self, data):
        #assert data is a User. Visitor pattern.
        values = {
                'name': data.name,
                'auth': 'password',
                'credential': None,
                'uid': self.uid,
                'sid': self.sid,
                #'metadata': data.metadata
            }
        status, resp =  self.ucengine.request('GET',
            '/user/%s?%s' % (data.name, urllib.urlencode({'uid':self.uid, 'sid': self.sid})))
        print("GET : ", status, resp)
        if status == 200:
            data.uid = resp['result']['uid']
            status, resp = self.ucengine.request('PUT',
                '/user/%s' % data.uid,
                unicode_urlencode(values)
            )
            assert status == 200
        else:
            status, resp = self.ucengine.request('POST',
                '/user',
                unicode_urlencode(values)
            )
            print status, resp
            assert status == 201
    def delete(self, data):
        if issubclass(data.__class__, User):
            status, resp = self.ucengine.request('DELETE',
                '/user/%s?%s' % (data.uid, urllib.urlencode({'uid':self.uid, 'sid': self.sid})))
            assert status == 200
    def users(self):
        status, resp = self.ucengine.request('GET',
            '/user?%s' % urllib.urlencode({
                'uid': self.uid,
                'sid': self.sid
        }))
        assert status == 200
        us = []
        for u in resp['result']:
            uu = User(u['name'])
            uu.uid = u['uid']
            uu.metadata = u['metadata']
            us.append(uu)
        return us


