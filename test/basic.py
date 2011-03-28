import sys
import unittest
sys.path.append('../src')
from ucengine import UCEngine, User

class TestBasic(unittest.TestCase):
	def setUp(self):
		self.uce = UCEngine('localhost', 5280)
		self.victor = User('victor.goya@af83.com')
		self.victor.presence(self.uce, 'pwd')
	def test_presence(self):
		self.assertTrue(None != self.victor.sid)
	def test_time(self):
		self.victor.time()
	def test_infos(self):
		infos = self.victor.infos()
		self.assertEquals(u'localhost', infos['domain'])

if __name__ == '__main__':
	unittest.main()