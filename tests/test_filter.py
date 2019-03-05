import util
import halibot
import unittest
import time

# Test that filters are applied correctly
class StubFilter(halibot.HalFilter):
	inited = False

	def init(self):
		self.ran = False
		self.inited = True

	def filter(self, msg):
		self.ran = True
		return msg

# Test if a filter properly accepts/drops messages
class StubRejectFilter(halibot.HalFilter):
	inited = False

	def init(self):
		self.accept = True
		self.inited = True

	def filter(self, msg):
		if self.accept:
			return msg
		return None

# Test if a filter properly mutates a msg.body
class StubBodyFilter(halibot.HalFilter):
	inited = False

	def init(self):
		self.inited = True
		self.ran = False

	def filter(self, msg):
		self.ran = True
		msg.body += "filtered"
		return msg

# --- Classes borrowed from test_core ---
class StubAgent(halibot.HalAgent):
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

# --- end borrow ---



class TestHalFilter(util.HalibotTestCase):

	def test_inbound_filter(self):
		# --- Borrowed from test_send_reply ---
		agent = StubAgent(self.bot)
		mod = StubReplier(self.bot)
		filter = StubFilter(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_module', mod)
		self.bot.add_instance('stub_filter', filter)

		self.assertTrue(agent.inited)
		self.assertTrue(mod.inited)
		self.assertTrue(filter.inited)

		self.assertTrue(agent.eventloop.is_running())
		self.assertTrue(mod.eventloop.is_running())
		self.assertTrue(filter.eventloop.is_running())

		foo = halibot.Message(body='foo')
		# --- end borrow ---

		self.bot.config["filters"] = {
			"inbound": {
				"stub_module": [ "stub_filter" ]
			}
		}

		agent.send_to(foo, ['stub_module'])

		util.waitOrTimeout(50, lambda: len(agent.received) != 0)

		self.assertEqual(len(agent.received), 1)
		self.assertEqual(agent.received[0].body, "foobar")
		self.assertTrue(filter.ran)


	def test_outbound_filter(self):
		agent = StubAgent(self.bot)
		mod = StubReplier(self.bot)
		filter = StubFilter(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_module', mod)
		self.bot.add_instance('stub_filter', filter)

		self.assertTrue(agent.inited)
		self.assertTrue(mod.inited)
		self.assertTrue(filter.inited)

		self.assertTrue(agent.eventloop.is_running())
		self.assertTrue(mod.eventloop.is_running())
		self.assertTrue(filter.eventloop.is_running())

		foo = halibot.Message(body='foo')

		self.bot.config["filters"] = {
			"outbound": {
				"stub_module": [ "stub_filter" ]
			}
		}

		agent.send_to(foo, ['stub_module'])

		util.waitOrTimeout(100, lambda: len(agent.received) != 0)

		self.assertEqual(len(agent.received), 1)
		self.assertEqual(agent.received[0].body, "foobar")
		self.assertTrue(filter.ran)

	def test_drop_filter(self):
		agent = StubAgent(self.bot)
		mod = StubReplier(self.bot)
		filter = StubRejectFilter(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_module', mod)
		self.bot.add_instance('stub_filter', filter)

		self.assertTrue(agent.inited)
		self.assertTrue(mod.inited)
		self.assertTrue(filter.inited)

		self.assertTrue(agent.eventloop.is_running())
		self.assertTrue(mod.eventloop.is_running())
		self.assertTrue(filter.eventloop.is_running())

		foo = halibot.Message(body='foo')

		self.bot.config["filters"] = {
			"inbound": {
				"stub_module": [ "stub_filter" ]
			}
		}

		filter.accept = False
		agent.send_to(foo, ['stub_module'])
		time.sleep(1)
		self.assertEqual(len(agent.received), 0)

		filter.accept = True
		agent.send_to(foo, ['stub_module'])
		util.waitOrTimeout(50, lambda: len(agent.received) != 0)
		self.assertEqual(len(agent.received), 1)

	def test_body_filter(self):
		agent = StubAgent(self.bot)
		mod = StubReplier(self.bot)
		filter = StubBodyFilter(self.bot)
		self.bot.add_instance('stub_agent', agent)
		self.bot.add_instance('stub_module', mod)
		self.bot.add_instance('stub_filter', filter)

		self.assertTrue(agent.inited)
		self.assertTrue(mod.inited)
		self.assertTrue(filter.inited)

		self.assertTrue(agent.eventloop.is_running())
		self.assertTrue(mod.eventloop.is_running())
		self.assertTrue(filter.eventloop.is_running())

		foo = halibot.Message(body='foo')

		self.bot.config["filters"] = {
			"outbound": {
				"stub_module": [ "stub_filter" ]
			}
		}

		agent.send_to(foo, ['stub_module'])

		util.waitOrTimeout(50, lambda: len(agent.received) != 0)

		self.assertEqual(len(agent.received), 1)
		self.assertEqual(agent.received[0].body, "foobarfiltered")
		self.assertTrue(filter.ran)

if __name__ == '__main__':
	unittest.main()
