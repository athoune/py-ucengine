__author__ = "mathieu@garambrogne.net"

from gevent import monkey
monkey.patch_all()

import urllib

from ucengine.meeting import Meetings

class User(object):
    "A user"
    def __init__(self, name):
        self.name = name
        self.metadata = {'nickname' : name}
        self.credential = None
        self.meetings = Meetings(self)
