
import unittest
from halibot.jsdict import jsdict

class TestJsdict(unittest.TestCase):

	def test_jsdict(self):
		d = jsdict()

		d.foo = 'iamblichus'
		self.assertEqual(d['foo'], 'iamblichus')
		self.assertEqual(d.foo, 'iamblichus')

		d['bar'] = 'porphyry'
		self.assertEqual(d['bar'], 'porphyry')
		self.assertEqual(d.bar, 'porphyry')

if __name__ == '__main__':
	unittest.main()
