# Test core halibot functionality

import time
import util
import halibot
import unittest

topic1_text = 'Help text one'
topic2_text = 'Help text two'

class StubModule(halibot.HalModule):
	inited = False

	topics = {
		'topic1': lambda: topic1_text,
		'topic2': topic2_text
	}

	def init(self):
		self.inited = True
		self.received = []
		self.received_mytype = []

	def receive(self, msg):
		self.received.append(msg)

	def receive_mytype(self, msg):
		self.received_mytype.append(msg)

class StubReplier(halibot.HalModule):
	inited = False

	def init(self):
		self.inited = True
		self.received = []

	def receive(self, msg):
		self.received.append(msg)
		self.reply(msg, body=msg.body + "bar")

class StubCommand(halibot.CommandModule):
	def init(self):
		self.commands = {
			"foo": self.foo,
			"bar": self.bar
		}
		self.foo_args = []
		self.bar_args = []

	def foo(self, args, msg=None):
		self.foo_args.append(args)
		self.reply(msg, body="fooed " + args)

	@halibot.AsArgs
	def bar(self, args, msg=None):
		self.bar_args.append(args)
		self.reply(msg, body="barred " + str(len(args)))

class StubAgent(halibot.HalAgent):
	inited = False

	def init(self):
		self.inited = True
		self.received = []

	def receive(self, msg):
		self.received.append(msg)

class TestCore(util.HalibotTestCase):

	def test_add_module(self):
		stub = StubModule(self.bot)
		self.bot.add_instance('stub_mod', stub)

		self.assertTrue(stub.inited)
		self.assertEqual(stub, self.bot.objects.get('stub_mod'))
		self.assertEqual(stub, self.bot.objects.modules.get('stub_mod'))
		self.assertEqual(len(self.bot.objects.agents.keys()), 0)


	def test_add_agent(self):
		stub = StubAgent(self.bot)
		self.bot.add_instance('stub_agent', stub)

		self.assertTrue(stub.inited)
		self.assertEqual(stub, self.bot.objects.get('stub_agent'))
		self.assertEqual(stub, self.bot.objects.agents.get('stub_agent'))
		self.assertEqual(len(self.bot.objects.modules.keys()), 0)

	def test_send_recv(self):
		agent = StubAgent(self.bot)
		mod = StubModule(self.bot)
		mod2 = StubModule(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_mod', mod)
		self.bot.add_instance('stub_mod2', mod2)

		# mod should receive: foo, bar, baz, qua
		# mod2 should receive: foo, bar, qua
		foo = halibot.Message(body='foo')
		bar = halibot.Message(body='bar')
		baz = halibot.Message(body='baz', origin='glub_agent')
		qua = halibot.Message(body='qua')
		qua2 = halibot.Message(body='qua', type='mytype')

		agent.dispatch(foo) # 0
		agent.send_to(bar, [ 'stub_mod/able', 'stub_mod2/baker' ] ) # 1
		self.bot.add_route('stub_agent', 'stub_mod')
		agent.dispatch(baz) # 2
		self.bot.add_route('stub_agent', 'stub_mod2')
		agent.dispatch(qua) # 3

		agent.dispatch(qua2) # 3

		util.waitOrTimeout(100, lambda: len(mod.received) == 4 and len(mod2.received) == 3 and len(mod.received_mytype) == 1 and len(mod2.received_mytype) == 1)

		# Check mod received mesages
		self.assertEqual(4, len(mod.received))
		self.assertEqual(foo.body, mod.received[0].body)
		self.assertEqual(bar.body, mod.received[1].body)
		self.assertEqual(baz.body, mod.received[2].body)
		self.assertEqual(qua.body, mod.received[3].body)
		self.assertEqual('', mod.received[0].whom())
		self.assertEqual('able', mod.received[1].whom())
		self.assertEqual('', mod.received[2].whom())
		self.assertEqual('', mod.received[3].whom())
		self.assertEqual('stub_mod', mod.received[0].target)
		self.assertEqual('stub_mod/able', mod.received[1].target)
		self.assertEqual('stub_mod', mod.received[2].target)
		self.assertEqual('stub_mod', mod.received[3].target)
		self.assertEqual('stub_agent', mod.received[0].origin)
		self.assertEqual('stub_agent', mod.received[1].origin)
		self.assertEqual('glub_agent', mod.received[2].origin)
		self.assertEqual('stub_agent', mod.received[3].origin)

		# Check mod2 received mesages
		self.assertEqual(3, len(mod2.received))
		self.assertEqual(foo.body, mod2.received[0].body)
		self.assertEqual(bar.body, mod2.received[1].body)
		self.assertEqual(qua.body, mod2.received[2].body)
		self.assertEqual('', mod.received[0].whom())
		self.assertEqual('able', mod.received[1].whom())
		self.assertEqual('', mod.received[2].whom())
		self.assertEqual('stub_mod2', mod2.received[0].target)
		self.assertEqual('stub_mod2/baker', mod2.received[1].target)
		self.assertEqual('stub_mod2', mod2.received[2].target)
		self.assertEqual('stub_agent', mod2.received[0].origin)
		self.assertEqual('stub_agent', mod2.received[1].origin)
		self.assertEqual('stub_agent', mod2.received[2].origin)

		# Check mytype messages
		self.assertEqual(1, len(mod.received_mytype))
		self.assertEqual(1, len(mod2.received_mytype))
		self.assertEqual(qua2.body, mod.received_mytype[0].body)
		self.assertEqual(qua2.body, mod2.received_mytype[0].body)


	def test_send_reply(self):
		agent = StubAgent(self.bot)
		mod = StubReplier(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_module', mod)

		self.assertTrue(agent.inited)
		self.assertTrue(mod.inited)

		self.assertTrue(agent.eventloop.is_running())

		foo = halibot.Message(body='foo')
		agent.send_to(foo, ['stub_module'])

		util.waitOrTimeout(100, lambda: len(agent.received) != 0)

		self.assertEqual(len(agent.received), 1)
		self.assertEqual(agent.received[0].body, "foobar")

	def test_sync_send(self):
		agent = StubAgent(self.bot)
		mod = StubReplier(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_module', mod)

		foo = halibot.Message(body='foo')
		rep = agent.sync_send_to(foo, ['stub_module'])

		self.assertEqual(rep["stub_module"][0].body, "foobar")

		with self.assertRaises(halibot.SyncSendSelfException):
			agent.sync_send_to(foo, ['stub_agent'])

	def test_help(self):
		agent = StubAgent(self.bot)
		mod = StubModule(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_module', mod)

		msgt0 = halibot.Message(type='help', body=[])
		msgt1 = halibot.Message(type='help', body=['topic1'])
		msgt2 = halibot.Message(type='help', body=['topic2'])

		self.assertEqual(set(agent.sync_send_to(msgt0, ['stub_module'])['stub_module'][0].body), set(['topic1', 'topic2']))
		self.assertEqual(agent.sync_send_to(msgt1, ['stub_module'])['stub_module'][0].body, topic1_text)
		self.assertEqual(agent.sync_send_to(msgt2, ['stub_module'])['stub_module'][0].body, topic2_text)

	def test_version_class(self):
		# Test major comparison
		self.assertTrue(halibot.Version("1.0.0") >= halibot.Version("0.1.0"))
		self.assertTrue(halibot.Version("0.1.0") <= halibot.Version("1.0.0"))
		self.assertTrue(halibot.Version("1.0.0") > halibot.Version("0.1.0"))
		self.assertTrue(halibot.Version("0.1.0") < halibot.Version("1.0.0"))

		# Test minor comparison
		self.assertTrue(halibot.Version("1.1.0") >= halibot.Version("1.0.0"))
		self.assertTrue(halibot.Version("1.0.0") <= halibot.Version("1.1.0"))
		self.assertTrue(halibot.Version("1.1.0") > halibot.Version("1.0.0"))
		self.assertTrue(halibot.Version("1.0.0") < halibot.Version("1.1.0"))

		# Test negatives of above
		self.assertFalse(halibot.Version("1.0.0") <= halibot.Version("0.1.0"))
		self.assertFalse(halibot.Version("0.1.0") >= halibot.Version("1.0.0"))
		self.assertFalse(halibot.Version("1.0.0") < halibot.Version("0.1.0"))
		self.assertFalse(halibot.Version("0.1.0") > halibot.Version("1.0.0"))

		self.assertFalse(halibot.Version("1.1.0") <= halibot.Version("1.0.0"))
		self.assertFalse(halibot.Version("1.0.0") >= halibot.Version("1.1.0"))
		self.assertFalse(halibot.Version("1.1.0") < halibot.Version("1.0.0"))
		self.assertFalse(halibot.Version("1.0.0") > halibot.Version("1.1.0"))

		# Test equalities
		self.assertEqual(halibot.Version("1.0.0"), halibot.Version("1.0.0"))
		self.assertNotEqual(halibot.Version("1.0.0"), halibot.Version("1.0.1"))
		self.assertNotEqual(halibot.Version("1.0.0"), halibot.Version("1.1.1"))
		self.assertNotEqual(halibot.Version("1.0.0"), halibot.Version("0.0.0"))

	def test_version_check(self):
		class VersionOkModule(halibot.HalModule):
			HAL_MINIMUM = "0.0.1"
			HAL_MAXIMUM = "1.0.0"

		class VersionFailMinModule(halibot.HalModule):
			HAL_MINIMUM = "1.0.0"
			HAL_MAXIMUM = "1.0.0"

		class VersionFailMaxModule(halibot.HalModule):
			HAL_MINIMUM = "0.0.1"
			HAL_MAXIMUM = "0.0.1"

		mod0 = VersionOkModule(self.bot) # Load ok
		mod1 = VersionFailMinModule(self.bot) # Fail minimum
		mod2 = VersionFailMaxModule(self.bot) # Fail maximum

		self.bot.VERSION = "0.1.0"

		self.assertTrue(self.bot._check_version(mod0))
		self.assertFalse(self.bot._check_version(mod1))
		self.assertFalse(self.bot._check_version(mod2))

		# Add the instances so they get cleaned up properly...
		self.bot.add_instance("mod0", mod0)
		self.bot.add_instance("mod1", mod1)
		self.bot.add_instance("mod2", mod2)

	def test_command(self):
		mod = StubCommand(self.bot)
		agent = StubAgent(self.bot)
		self.bot.add_instance('stub_cagent', agent)
		self.bot.add_instance('stub_cmodule', mod)

		# Test regular bare string args
		foo = halibot.Message(body='foo')
		cmdfoo = halibot.Message(body='!foo')
		cmdfoo2 = halibot.Message(body='!foo moo')

		# Test AsArgs arg splitting
		bar = halibot.Message(body='bar')
		cmdbar = halibot.Message(body='!bar')
		cmdbar2 = halibot.Message(body='!bar moo')
		cmdbar3 = halibot.Message(body='!bar moo foo')

		# Test unhandled command
		baz = halibot.Message(body="!baz")

		agent.dispatch(foo)
		agent.dispatch(cmdfoo)
		agent.dispatch(cmdfoo2)

		util.waitOrTimeout(100, lambda: len(agent.received) == 2)

		self.assertEqual(2, len(agent.received))
		self.assertEqual("fooed ", agent.received[0].body)
		self.assertEqual("", mod.foo_args[0])
		self.assertEqual("fooed moo", agent.received[1].body)
		self.assertEqual("moo", mod.foo_args[1])

		agent.received = []

		agent.dispatch(bar)
		agent.dispatch(cmdbar)
		agent.dispatch(cmdbar2)
		agent.dispatch(cmdbar3)

		util.waitOrTimeout(100, lambda: len(agent.received) == 3)

		self.assertEqual(3, len(agent.received))
		self.assertEqual("barred 1", agent.received[0].body)
		self.assertEqual([""], mod.bar_args[0])
		self.assertEqual("barred 1", agent.received[1].body)
		self.assertEqual(["moo"], mod.bar_args[1])
		self.assertEqual("barred 2", agent.received[2].body)
		self.assertEqual(["moo", "foo"], mod.bar_args[2])

		agent.received = []

		agent.sync_send_to(baz, [ 'stub_cmodule' ])

		self.assertEqual(0, len(agent.received))

	def test_restart(self):
		mod = StubModule(self.bot)
		mod2 = StubModule(self.bot)

		self.bot.add_instance("stub_module", mod)
		self.bot.add_instance("stub_module2", mod2)

		# .inited should be reset to True if module was restarted
		mod.inited = False
		mod2.inited = False  #...but this module should be unaffected

		self.bot.restart("stub_module")
		self.bot.restart("nope")

		self.assertTrue(mod.inited)
		self.assertFalse(mod2.inited)

	def test_invoke(self):
		class InvokeModule(halibot.HalModule):
			def receive(self, msg):
				ret = self.invoke("stub_target","target", msg.body, foo=msg.body)
				self.reply(msg, body="target said: " + msg.body)
		class TargetModule(halibot.HalModule):
			def init(self):
				self.invoked = False
			def target(self, *args, **kwargs):
				self.invoked = True
				return " ".join(args) + " " + " ".join(kwargs.keys())

		inv = InvokeModule(self.bot)
		tar = TargetModule(self.bot)
		agent = StubAgent(self.bot)

		self.bot.add_instance("stub_invoker", inv)
		self.bot.add_instance("stub_target", tar)
		self.bot.add_instance("stub_agent", agent)

		agent.dispatch(halibot.Message(body="bar"))

		util.waitOrTimeout(100, lambda: len(agent.received) != 0)

		self.assertTrue(tar.invoked)
		self.assertEqual(1, len(agent.received))
		self.assertTrue("target said: bar foo")

	def test_module_fail_recover(self):
		class ExceptionModule(halibot.HalModule):
			def init(self):
				self.received = []
			def receive(self, msg):
				self.received.append(msg)
				if msg.body == "explode":
					raise NotImplementedError()

		agent = StubAgent(self.bot)
		mod = ExceptionModule(self.bot)

		self.bot.add_instance("stub_agent", agent)
		self.bot.add_instance("stub_mod", mod)

		self.assertEqual(0, len(agent.received))

		agent.dispatch(halibot.Message(body="foo"))
		util.waitOrTimeout(100, lambda: len(mod.received) == 1)
		self.assertEqual(1, len(mod.received))
		self.assertEqual("foo", mod.received[0].body)

		agent.dispatch(halibot.Message(body="explode"))
		util.waitOrTimeout(100, lambda: len(mod.received) == 2)
		self.assertEqual(2, len(mod.received))
		self.assertEqual("explode", mod.received[1].body)

		agent.dispatch(halibot.Message(body="foo"))
		util.waitOrTimeout(100, lambda: len(mod.received) == 3)
		self.assertEqual(3, len(mod.received))
		self.assertEqual("foo", mod.received[2].body)


if __name__ == '__main__':
	unittest.main()
