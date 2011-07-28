import sys
import time
import unittest
import os.path
sys.path.insert(1, os.path.abspath('src'))
from ucengine import UCEngine, User, UCError

class TestBasic(unittest.TestCase):

    def setUp(self):
        self.uce = UCEngine('localhost', 5280)
        self.victor = User('participant')
        self.session = self.uce.connect(self.victor, 'pwd').loop()

    def tearDown(self):
        self.session.close()

    def test_presence(self):
        self.assertTrue(None != self.session.sid)

    def test_bad_presence(self):
        thierry = User('thierry')
        try:
            self.uce.connect(thierry, '****')
        except UCError as e:
            self.assertEquals(404, e.code)
        else:
            self.assertTrue(False)

    def test_time(self):
        time = self.session.time()
    """
    # Officialy bugged
    def test_infos(self):
        infos = self.session.infos()
        self.assertEquals(u'localhost', infos['domain'])

    def test_meeting(self):
        thierry = User('participant2')
        sthierry = self.uce.connect(thierry, 'pwd')
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
        #self.assertEquals(
        #    set([u'#ucengine', u'#af83']),
        #    self.victor.meetings[SESSION].twitter_hash_tags)

if __name__ == '__main__':
    unittest.main()
