import sys
import time
import unittest
sys.path.append('../src')
from ucengine import UCEngine, User, UCError

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.uce = UCEngine('localhost', 5280)
        self.victor = User('victor.goya@af83.com')
        self.victor.presence(self.uce, 'pwd')
    def tearDown(self):
        self.victor.unpresence()
    def test_presence(self):
        self.assertTrue(None != self.victor.sid)
    def test_bad_presence(self):
        thierry = User('thierry.bomandouki@af83.com')
        try:
            thierry.presence(self.uce, '****')
        except UCError as e:
            self.assertEquals(403, e.code)
        else:
            self.assertTrue(False)
    def test_time(self):
        time = self.victor.time()
    def test_infos(self):
        infos = self.victor.infos()
        self.assertEquals(u'localhost', infos['domain'])
    def test_meeting(self):
        thierry = User('thierry.bomandouki@af83.com')
        thierry.presence(self.uce, 'pwd')
        SESSION = 'demo'
        MSG = u"Bonjour monde"
        def _m(event):
            self.assertEquals(event['metadata']['text'], MSG)
            #print event
        self.victor.meetings[SESSION].callback('chat.message.new', _m).join()
        thierry.meetings[SESSION].callback('chat.message.new', _m).join()
        thierry.meetings[SESSION].chat(MSG, 'fr')
        self.victor.meetings[SESSION].async_chat(MSG, 'fr')
        time.sleep(0.1) # waiting for events
        # [FIXME] roster returns now uid, not name
        # self.assertEquals(
        #     set([u'victor.goya@af83.com', u'thierry.bomandouki@af83.com']),
        #     self.victor.meetings[SESSION].roster)
        self.assertEquals(
            set([u'#ucengine', u'#af83']),
            self.victor.meetings[SESSION].twitter_hash_tags)


if __name__ == '__main__':
    unittest.main()