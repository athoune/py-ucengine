__author__ = "mathieu@garambrogne.net"

class Client(object):
    "A simple client"

    def __init__(self, name, uid=None, credential=None, metadata={}):
        self.name = name
        self.metadata = metadata
        self.credential = credential
        self.uid = uid

class User(Client):
    "A user"

    def __init__(self, name, uid=None, credential=None, metadata={}):
        if metadata.has_key('nickname'):
            metadata['nickname'] = name
        Client.__init__(self, name, uid, credential, metadata)

    def __repr__(self):
        return "<User name:%s>" % self.name

