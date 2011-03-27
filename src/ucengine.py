#!/usr/bin/env python

__author__ = "mathieu@garambrogne.net"

import json
import time

from gevent import monkey
import gevent

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
				urllib.urlencode(body))
		else:
			connection.request(method, '/api/0.4/%s' % path)
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
			self._event()
	def _listen(self, start=None):
		status, p = self.ucengine.request('GET', 'event?%s' % urllib.urlencode({
			'uid': self.uid,
			'sid': self.sid,
			'_async': 'lp',
			'start': start
		}))
		self.onEvent((status, p))
		self._event(int(time.time()))
	def _event(self, start=None):
		if start == None:
			start = int(time.time())
		gevent.spawn(self._listen, start)
	def onEvent(self, resp):
		time.sleep(2)
		print resp
	def time(self):
		status, p = self.ucengine.request('GET', 'time?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		return p['result']
	def infos(self):
		status, p = self.ucengine.request('GET', 'infos?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		return p['result']

if __name__ == '__main__':
	#launch demo:start(). on the server
	ucengine = UCEngine('localhost', 5280)
	victor = User('victor.goya@af83.com')
	victor.presence(ucengine, 'pwd')
	time.sleep(1)
	print victor.time()
	time.sleep(1)
	print victor.infos()
time.sleep(10)