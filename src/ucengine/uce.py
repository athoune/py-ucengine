import httplib
import urllib
import json

from core import UCError
from session import Session

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
        try:
            response = json.loads(raw)
        except ValueError as e:
            print raw
            response = None
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


