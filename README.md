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

Code
----

Validated with pyflakes and pylint -d W0312 (I love tabs)
