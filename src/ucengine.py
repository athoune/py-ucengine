import json

from gevent import monkey

monkey.patch_all();

import httplib
import urllib

class UCEngine(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.users = []
	def request(self, method, path, body=None):
		connection = httplib.HTTPConnection(self.host, self.port)
		if body != None:
			connection.request(method, '/api/0.4/%s' % path,
				urllib.urlencode(body),headers = {'Host': 'localhost'})
		else:
			connection.request(method, '/api/0.4/%s' % path,
				headers = {'Host': 'localhost'})
		r = connection.getresponse()
		response = json.loads(r.read())
		connection.close()
		return r.status, response

class User(object):
	def __init__(self, uid):
		self.uid = uid
	def presence(self, uce, credential):
		self.ucengine = uce
		status, p = self.ucengine.request('POST','presence/', {
			'uid':self.uid,
			'credential':credential,
			'metadata[nickname]': self.uid}
			)
		if status == 201:
			self.sid = p['result']
	def time(self):
		status, p = self.ucengine.request('GET', 'time?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		return p['result']
	def infos(self):
		status, p = self.ucengine.request('GET', 'infos?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		return p['result']

ucengine = UCEngine('192.168.1.142', 5280)
victor = User('victor.goya@af83.com')
victor.presence(ucengine, 'pwd')
print victor.time()
print victor.infos()