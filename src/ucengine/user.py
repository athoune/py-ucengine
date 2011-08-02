__author__ = "mathieu@garambrogne.net"

from gevent import monkey
monkey.patch_all()

import urllib

class User(object):
    "A user"

    def __init__(self, name, uid=None, credential=None, metadata={}):
        self.name = name
        self.metadata = {'nickname' : name}
        self.credential = credential
        self.uid = uid

    def __repr__(self):
        return "<User name:%s>" % self.name
