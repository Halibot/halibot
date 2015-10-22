# Test core halibot functionality

import util
import halibot
import unittest

class StubModule(halibot.HalModule):
	inited = False

	def init(self):
		self.inited = True


class StubAgent(halibot.HalAgent):
	inited = False

	def init(self):
		self.inited = True

class TestCore(util.HalibotTestCase):

	def test_add_module(self):
		stub = StubModule(self.bot)
		self.bot.add_module_instance('stub_mod', stub)

		self.assertTrue(stub.inited)
		self.assertEqual(stub, self.bot.get_object('stub_mod'))

	def test_add_agent(self):
		stub = StubAgent(self.bot)
		self.bot.add_agent_instance('stub_agent', stub)

		self.assertTrue(stub.inited)
		self.assertEqual(stub, self.bot.get_object('stub_agent'))

if __name__ == '__main__':
	unittest.main()

