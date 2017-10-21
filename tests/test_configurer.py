
import util
import halibot
import unittest
from unittest.mock import patch


class TestConfigurer(unittest.TestCase):

	@patch('halibot.halconfigurer.get_input', return_value='bar')
	def test_optionString_str(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionString('foo', default="foo")
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], "bar")

	@patch('halibot.halconfigurer.get_input', return_value=2)
	def test_optionInt_int(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionInt('foo', default=1)
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], 2)

	@patch('halibot.halconfigurer.get_input', return_value="2")
	def test_optionInt_str(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionInt('foo', default=1)
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], 2)

	@patch('halibot.halconfigurer.get_input', return_value=None)
	def test_optionInt_none(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionInt('foo', default=1)
		c = Configurer()
		try:
			c.configure()
		except TypeError as e:
			# Yay, we type errored as expected
			return

		self.assertTrue(False)

	@patch('halibot.halconfigurer.get_input', return_value=2.1)
	def test_optionNumber_int(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionNumber('foo', default=1.0)
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], 2.1)

	@patch('halibot.halconfigurer.get_input', return_value="2")
	def test_optionNumber_str(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionNumber('foo', default=1.0)
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], 2)

	@patch('halibot.halconfigurer.get_input', return_value=None)
	def test_optionNumber_none(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionNumber('foo', default=1.0)
		c = Configurer()
		try:
			c.configure()
		except TypeError as e:
			# Yay, we type errored as expected
			return

		self.assertTrue(False)

	@patch('halibot.halconfigurer.get_input', return_value=True)
	def test_optionBoolean_true(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionBoolean('foo', default=False)
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], True)

	@patch('halibot.halconfigurer.get_input', return_value=False)
	def test_optionBoolean_false(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionBoolean('foo', default=True)
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], False)

	@patch('halibot.halconfigurer.get_input', return_value="TrUe")
	def test_optionBoolean_strTrue(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionBoolean('foo', default=False)
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], True)

	@patch('halibot.halconfigurer.get_input', return_value="FaLsE")
	def test_optionBoolean_strFalse(self, input):
		class Configurer(halibot.HalConfigurer):
			def configure(self):
				self.optionBoolean('foo', default=True)
		c = Configurer()
		c.configure()

		self.assertTrue('foo' in c.options)
		self.assertEqual(c.options['foo'], False)



if __name__ == '__main__':
	unittest.main()
