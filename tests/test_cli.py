import unittest
import os, sys, shutil
import subprocess, tempfile
import json

class CliTestCase(unittest.TestCase):
	def setUp(self):
		self.path = tempfile.mkdtemp(prefix='halibot-test')
		self.mainPy = os.path.join(os.getcwd(), 'main.py')
		os.chdir(self.path)

	def tearDown(self):
		os.chdir(os.path.dirname(self.mainPy))
		shutil.rmtree(self.path)

	# Run a halibot CLI command
	def cmd(self, args, input=None):
		args = [sys.executable, self.mainPy] + args
		proc = subprocess.run(args, input=input, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		self.assertEqual(proc.returncode, 0)
		return proc

class TestInit(CliTestCase):

	def test_init(self):
		# Create the config.json with 'halibot init'
		self.assertFalse(os.path.exists('config.json'))
		self.assertFalse(os.path.exists('packages'))
		self.cmd(['init'])
		self.assertTrue(os.path.exists('config.json'))
		self.assertTrue(os.path.exists('packages'))

		with open('config.json') as f:
			# Verify that the config looks vaguely right
			conf = json.load(f)
			self.assertTrue('agent-instances' in conf)
			self.assertTrue('module-instances' in conf)
			self.assertTrue('package-path' in conf)
			self.assertTrue(len(conf['package-path']) > 0)
"""
# Disabled for now, since halibot.fish is RIP
class TestFetch(CliTestCase):

	def test_fetch(self):
		ircPath = os.path.join('packages', 'irc')

		self.cmd(['init'])
		self.assertFalse(os.path.exists(ircPath))
		self.cmd(['fetch', 'irc'])
		self.assertTrue(os.path.exists(ircPath))
		self.cmd(['unfetch', 'irc'])
		self.assertFalse(os.path.exists(ircPath))
"""
class TestInstall(CliTestCase):

	def test_install(self):
		ircPath = os.path.join('packages', 'irc')

		self.cmd(['init'])

		with open('config.json') as f:
			conf = json.load(f)
			self.assertFalse('hello0' in conf['module-instances'])

		self.cmd(['add', 'hello'], input='hello0\n')

		with open('config.json') as f:
			conf = json.load(f)
			self.assertTrue('hello0' in conf['module-instances'])
			self.assertEqual('hello:Default', conf['module-instances']['hello0']['of'])

		self.cmd(['rm', 'hello0'])

		with open('config.json') as f:
			conf = json.load(f)
			self.assertFalse('hello0' in conf['module-instances'])

		self.assertFalse(os.path.exists(ircPath))


if __name__ == '__main__':
	unittest.main()
