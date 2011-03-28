import sys
import unittest
sys.path.append('../src')
from ucengine import UCEngine, User, Meeting

class TestBasic(unittest.TestCase):
	def setUp(self):
		self.uce = UCEngine('localhost', 5280)
		self.victor = User('victor.goya@af83.com')
		self.victor.presence(self.uce, 'pwd')
	def tearDown(self):
		self.victor.unpresence()
	def test_presence(self):
		self.assertTrue(None != self.victor.sid)
	def test_time(self):
		time = self.victor.time()
	def test_infos(self):
		infos = self.victor.infos()
		self.assertEquals(u'localhost', infos['domain'])
	def test_meeting(self):
		thierry = User('thierry.bomandouki@af83.com')
		thierry.presence(self.uce, 'pwd')
		self.victor.join(Meeting('demo'))
		thierry.join(Meeting('demo'))
		thierry.meetings['demo'].chat("Bonjour monde", 'fr')

if __name__ == '__main__':
	unittest.main()