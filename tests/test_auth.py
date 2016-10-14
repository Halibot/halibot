# Test core halibot functionality

import time
import util
import halibot
import unittest

class StubModuleFunc(halibot.HalModule):

	def init(self):
		self.called = False

	def function(self, msg):
		self.called = True

	def receive(self, msg):
		if self.hasPermission(msg, "Foo"):
			self.function(msg)

class StubModuleDec(halibot.HalModule):

	def init(self):
		self.called = False
	
	@halibot.halauth.hasPermission("Foo")
	def function(self, msg):
		self.called = True

	def receive(self, msg):
		self.function(msg)

class TestAuth(util.HalibotTestCase):

	def test_hasperm_func(self):
		self.bot.auth.enabled = True
		stub = StubModuleFunc(self.bot)
		self.bot.add_module_instance('stub_mod', stub)

		ri = "test/foobar"
		user = "tester"
		perm = "Foo"
		msg = halibot.Message(body="", origin=ri, author=user)

		stub.receive(msg)
	
		self.assertFalse(stub.called)

		self.bot.auth.grantPermission(ri, user, perm)
		stub.receive(msg)

		self.assertTrue(stub.called)

	def test_hasperm_dec(self):
		self.bot.auth.enabled = True
		stub = StubModuleDec(self.bot)
		self.bot.add_module_instance('stub_mod', stub)

		ri = "test/foobar"
		user = "tester"
		perm = "Foo"
		msg = halibot.Message(body="", origin=ri, author=user)

		stub.receive(msg)
	
		self.assertFalse(stub.called)

		self.bot.auth.grantPermission(ri, user, perm)
		stub.receive(msg)

		self.assertTrue(stub.called)



if __name__ == '__main__':
	unittest.main()

