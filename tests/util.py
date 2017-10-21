# Utilities to assist in writing tests

import halibot
import unittest
import logging
import time

def waitOrTimeout(timeout, condition):
	for i in range(timeout):
		if condition():
			break
		time.sleep(0.1)
	else:
		print("warning: timeout reached") # pragma: no cover


# Provides a unique bot in self.bot for every test case
class HalibotTestCase(unittest.TestCase):

	def setUp(self):
		# Silence expected error messages
		logging.basicConfig(level=logging.CRITICAL)
		self.bot = halibot.Halibot(use_config=False)

	def tearDown(self):
		self.bot.shutdown()
