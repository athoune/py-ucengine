#!/usr/bin/env python

__author__ = "mathieu@garambrogne.net"

import json
import time

from gevent import monkey
import gevent

monkey.patch_all();

import httplib
import urllib

class UCError(Exception):
	def __init__(self, value):
		self.value = value
	def __repr__(self):
		return "<UCError %s>" % self.value

class UCEngine(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.users = []
	def request(self, method, path, body=None):
		connection = httplib.HTTPConnection(self.host, self.port)
		if body != None:
			connection.request(method, '/api/0.4%s' % path,
				urllib.urlencode(body))
		else:
			connection.request(method, '/api/0.4%s' % path)
		r = connection.getresponse()
		response = json.loads(r.read())
		connection.close()
		return r.status, response

class User(object):
	def __init__(self, uid):
		self.uid = uid
		self.event_pid = None
	#def __del__(self):
	#	if self.event_pid != None:
	#		self.unpresence()
	def presence(self, uce, credential):
		self.ucengine = uce
		status, p = self.ucengine.request('POST','/presence/', {
			'uid':self.uid,
			'credential':credential,
			'metadata[nickname]': self.uid}
			)
		if status == 201:
			self.sid = p['result']
			self.event_pid = gevent.spawn(self._listen)
		else:
			raise UCError(p)
	def unpresence(self):
		status, p = self.ucengine.request('DELETE','/presence/%s?%s' % (self.sid, urllib.urlencode({
			'uid': self.uid,
			'sid': self.sid}))
			)
		if status != 200:
			raise UCError(p)
		self.event_pid.kill()
	def _listen(self):
		start = int(time.time())
		while True:
			status, p = self.ucengine.request('GET', '/event?%s' % urllib.urlencode({
				'uid': self.uid,
				'sid': self.sid,
				'_async': 'lp',
				'start': start
				}))
			start = int(time.time())
			self.onEvent((status, p))
	def onEvent(self, resp):
		print resp
	def time(self):
		status, p = self.ucengine.request('GET', '/time?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		return p['result']
	def infos(self):
		status, p = self.ucengine.request('GET', '/infos?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		return p['result']
