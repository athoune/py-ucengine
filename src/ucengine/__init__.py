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
	def __init__(self, code, value):
		self.code = code
		self.value = value
	def __repr__(self):
		return "<UCError:%i %s>" % (self.code, self.value)

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
		self.meetings = {}
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
			raise UCError(status, p)
	def unpresence(self):
		status, p = self.ucengine.request('DELETE','/presence/%s?%s' % (self.sid, urllib.urlencode({
			'uid': self.uid,
			'sid': self.sid}))
			)
		if status != 200:
			raise UCError(status, p)
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
			if status == 200:
				for event in p['result']:
					self.onEvent(event['type'], event)
	def onEvent(self, type, event):
		print event
	def time(self):
		status, p = self.ucengine.request('GET', '/time?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		return p['result']
	def infos(self):
		status, p = self.ucengine.request('GET', '/infos?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		return p['result']
	def join_meeting(self, meeting):
		Meeting(meeting)._join(self)

class Meeting(object):
	def __init__(self, meeting):
		self.meeting = meeting
		self.callbacks = {}
	def _join(self, user):
		status, p = user.ucengine.request('POST', '/meeting/all/%s/roster/' % self.meeting, {
			'uid': user.uid,
			'sid': user.sid
		})
		assert status == 200
		self.ucengine = user.ucengine
		self.user = user
		user.meetings[self.meeting] = self
		self.event_pid = gevent.spawn(self._listen)
	def _listen(self):
		start = 0
		while True:
			status, p = self.ucengine.request('GET', '/event/%s?%s' % (self.meeting, urllib.urlencode({
				'uid': self.user.uid,
				'sid': self.user.sid,
				'_async': 'lp',
				'start': start
				})))
			if status == 200:
				for event in p['result']:
					start = event['datetime'] + 1
					self.onEvent(event['type'], event)
	def onEvent(self, type_, event):
		if type_ in self.callbacks:
			self.callbacks[type_](event)
		# else:
		# 	print type_
	def chat(self, text, lang='en'):
		status, p = self.ucengine.request('POST', '/event/%s' % self.meeting, {
			'uid': self.user.uid,
			'sid': self.user.sid,
			'type': 'chat.message.new',
			'metadata[lang]': lang,
			'metadata[text]': text
		})
		assert status == 201
		return p['result']
