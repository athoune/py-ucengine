UCEngine API for Python
=======================

A python client for UCEngine.
Async is handled with [gevent](http://www.gevent.org/).

Status
------

Minimalistic implementation.

Install
-------

	python setup.py build
	sudo python setup.py install

Test
----

Lauch the server (Erlang side)

	demo:start().

And the test (Python side)

	python test/basic.py

API
---

	# an engine
	uce = UCEngine('localhost', 5280)
	# a user
	victor = User('victor.goya@af83.com')
	# connecting
	victor.presence(uce, 'pwd')
	# asking hour to the server
	print victor.time()
	# registering callback. Meeting creation is lazy
	victor.meetings['demo'].callback('chat.message.new', lambda event: print event)
	# joining
	victor.meetings['demo'].join()
	# fire and forget a message
	victor.meetings['demo'].async_chat('bonjour Monde', 'fr')

The callback should print the event

Code
----

Validated with pyflakes and pylint
