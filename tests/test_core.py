# Test core halibot functionality

import time
import util
import halibot
import unittest

class StubModule(halibot.HalModule):
	inited = False

	def init(self):
		self.inited = True
		self.received = []

	def receive(self, msg):
		self.received.append(msg)

class StubReplier(halibot.HalModule):
	inited = False

	def init(self):
		self.inited = True
		self.received = []

	def receive(self, msg):
		self.received.append(msg)
		self.reply(msg, body=msg.body + "bar")

class StubAgent(halibot.HalAgent):
	inited = False

	def init(self):
		self.inited = True

class TestCore(util.HalibotTestCase):

	def test_add_module(self):
		stub = StubModule(self.bot)
		self.bot.add_instance('stub_mod', stub)

		self.assertTrue(stub.inited)
		self.assertEqual(stub, self.bot.objects.get('stub_mod'))

	def test_add_agent(self):
		stub = StubAgent(self.bot)
		self.bot.add_instance('stub_agent', stub)

		self.assertTrue(stub.inited)
		self.assertEqual(stub, self.bot.objects.get('stub_agent'))

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

		agent.dispatch(foo) # 0
		agent.send_to(bar, [ 'stub_mod/able', 'stub_mod2/baker' ] ) # 1
		agent.connect(mod)
		agent.dispatch(baz) # 2
		agent.connect(mod2)
		agent.dispatch(qua) # 3

		# TODO do something sensible here
		timeout = 10
		increment = .1
		while timeout > 0 and len(mod.received) != 4 and len(mod2.received) != 3:
			time.sleep(increment)
			timeout -= increment

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

	def test_sync_send(self):
		agent = StubAgent(self.bot)
		mod = StubReplier(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_module', mod)

		foo = halibot.Message(body='foo')
		rep = agent.sync_send_to(foo, ['stub_module'])

		self.assertEqual(rep["stub_module"][0].body, "foobar")

if __name__ == '__main__':
	unittest.main()
