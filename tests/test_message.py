import util
import halibot
import unittest

testMessage = halibot.Message(body="foo", type="bar", author="Foo Barrington", identity="yes", origin="Assyria", misc="[\"foo\", \"bar\"]", target="bees?")

class TestMessage(util.HalibotTestCase):
	def testCreation(self):
		self.assertEqual("foo", testMessage.body)
		self.assertEqual("bar", testMessage.type)
		self.assertEqual("Foo Barrington", testMessage.author)
		self.assertEqual("yes", testMessage.identity)
		self.assertEqual("Assyria", testMessage.origin)
		self.assertEqual("[\"foo\", \"bar\"]", testMessage.misc)
		self.assertEqual("bees?", testMessage.target)

	# Test that repr will eval to a duplicate message
	def testRepr(self):
		m = eval(testMessage.__repr__())

		self.assertEqual("foo", m.body)
		self.assertEqual("bar", m.type)
		self.assertEqual("Foo Barrington", m.author)
		self.assertEqual("yes", m.identity)
		self.assertEqual("Assyria", m.origin)
		self.assertEqual("[\"foo\", \"bar\"]", m.misc)
		self.assertEqual("bees?", m.target)

if __name__ == '__main__':
	unittest.main()
