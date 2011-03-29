"""
Client for UCEngine
"""

__author__ = "mathieu@garambrogne.net"

import json
import time

from gevent import monkey
import gevent

monkey.patch_all()

import httplib
import urllib

class UCError(Exception):
	"Standard error coming from the server"
	def __init__(self, code, value):
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
			connection.request(method, '/api/0.4%s' % path,
				urllib.urlencode(body))
		else:
			connection.request(method, '/api/0.4%s' % path)
		resp = connection.getresponse()
		response = json.loads(resp.read())
		connection.close()
		return resp.status, response

class Meetings(object):
	"Lazy dictionnary for handling meetings"
	def __init__(self, user):
		self.meetings = {}
		self.user = user
	def __getitem__(self, meeting):
		if not meeting in self.meetings:
			self.meetings[meeting] = Meeting(meeting)
			self.meetings[meeting].ucengine = self.user.ucengine
			self.meetings[meeting].user = self.user
		return self.meetings[meeting]

class Eventualy(object):
	"Dummy object implementing event loop"
	def __init__(self):
		self.callbacks = {}
		self.event_pid = None
		self.ucengine = None
	def callback(self, key, cback):
		"register a new callback"
		self.callbacks[key] = cback
	def event_loop(self, url):
		"launch the backround event listening"
		def _listen():
			start = 0
			while True:
				status, resp = self.ucengine.request('GET', "%s&start=%i" % (url, start))
				if status == 200:
					for event in resp['result']:
						start = event['datetime'] + 1
						if event['type'] in self.callbacks:
							gevent.spawn(self.callbacks[event['type']], event)
						else:
							print event['type'], event
		self.event_pid = gevent.spawn(_listen)
	def event_stop(self):
		"stop the event loop"
		self.event_pid.kill()

class User(Eventualy):
	"A user"
	def __init__(self, uid):
		Eventualy.__init__(self)
		self.uid = uid
		self.sid = None
		self.meetings = Meetings(self)
	#def __del__(self):
	#	if self.event_pid != None:
	#		self.unpresence()
	def presence(self, uce, credential):
		"I'm coming"
		self.ucengine = uce
		status, resp = self.ucengine.request('POST', '/presence/', {
			'uid':self.uid,
			'credential':credential,
			'metadata[nickname]': self.uid}
			)
		if status == 201:
			self.sid = resp['result']
			self.event_loop('/event?%s' % urllib.urlencode({
				'uid': self.uid,
				'sid': self.sid,
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
		if status != 200:
			raise UCError(status, resp)
		self.event_stop()
	def time(self):
		"What time is it"
		status, resp = self.ucengine.request('GET', '/time?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		assert status == 200
		return resp['result']
	def infos(self):
		"Infos about the server"
		status, resp = self.ucengine.request('GET', '/infos?%s' % urllib.urlencode({
			'uid': self.uid, 'sid': self.sid}))
		assert status == 200
		return resp['result']

class Meeting(Eventualy):
	"A meeting (a room)"
	def __init__(self, meeting):
		Eventualy.__init__(self)
		self.user = None
		self.meeting = meeting
		self.roster = set()
		self.twitter_hash_tags = set()
		self.callbacks = {
			'internal.roster.add': lambda event: self.roster.add(event['from']),
			'internal.roster.delete': lambda event: self.roster.remove(
				event['from']),
			'twitter.hashtag.add': lambda event: self.twitter_hash_tags.add(
				event['metadata']['hashtag'])
		}
	def join(self):
		"Joining the meeting"
		status, resp = self.ucengine.request('POST',
			'/meeting/all/%s/roster/' % self.meeting, {
				'uid': self.user.uid,
				'sid': self.user.sid
		})
		assert status == 200
		self.event_loop('/event/%s?%s' % (self.meeting, urllib.urlencode({
			'uid': self.user.uid,
			'sid': self.user.sid,
			'_async': 'lp'
		})))
	def chat(self, text, lang='en'):
		"Talking to the meeting"
		status, resp = self.ucengine.request('POST',
			'/event/%s' % self.meeting, {
				'uid': self.user.uid,
				'sid': self.user.sid,
				'type': 'chat.message.new',
				'metadata[lang]': lang,
				'metadata[text]': text
			})
		assert status == 201
		return resp['result']
	def async_chat(self, text, lang='en'):
		gevent.spawn(self.chat, text, lang)
