UCEngine API for Python
=======================

A python client for UCEngine.
Async is handled with [gevent](http://www.gevent.org/).

Status
------

early alpha.

Install
-------

	python setup.py build
	sudo python setup.py install

Test
----

Lauch the server (Erlang side)

	demo:start().

And the test (Python side)

	cd test
	python basic.py

API
---

	uce = UCEngine('localhost', 5280)
	victor = User('victor.goya@af83.com')
	victor.presence(uce, 'pwd')
	print victor.time()
	victor.meetings['demo'].callback('chat.message.new', lambda event: print event)
	victor.meetings['demo'].join()
	victor.meetings['demo'].async_chat('bonjour Monde', 'fr')

Code
----

Validated with pyflakes and pylint -d W0312 (I love tabs)
