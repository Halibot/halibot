# Utilities to assist in writing tests

import halibot
import unittest
import logging

# Provides a unique bot in self.bot for every test case
class HalibotTestCase(unittest.TestCase):

	def setUp(self):
		# Silence expected error messages
		logging.basicConfig(level=logging.CRITICAL)
		self.bot = halibot.Halibot(use_config=False)

	def tearDown(self):
		self.bot.shutdown()
