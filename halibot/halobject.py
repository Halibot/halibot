import logging
import asyncio
import inspect
import copy
from threading import Thread
from collections import defaultdict
from .halconfigurer import HalConfigurer
from .message import MalformedMsgException

class SyncSendSelfException(Exception): 'Cannot sync_send_to oneself.'

class HalObject():

	def __init__(self, hal, conf={}):
		self._hal = hal
		self.config = conf
		self.log = logging.getLogger(self.__class__.__name__) # TODO: Put instantiated name in here too

		# Only used in HalModule.reply right now, but accessed on potentially any
		# HalObject, so it exists on every HalObject to avoid attribute errors
		self.sync_replies = defaultdict(lambda: []) # UUID -> [Message, ...]

		self.eventloop = asyncio.SelectorEventLoop()
		self._thread = Thread(target=self._run_eventloop)
		self._thread.start()

	def _run_eventloop(self):
		self.eventloop.run_forever()
		self.eventloop.close()

	def _shutdown(self):
		self.eventloop.call_soon_threadsafe(self.eventloop.stop)
		self._thread.join()
		self.shutdown()

	def _queue_msg(self, msg):
		fut = asyncio.run_coroutine_threadsafe(self._receive(msg), self.eventloop)
		return fut

	def init(self):
		pass

	def shutdown(self):
		pass

	def apply_filter(self, dest):
		fl = self._hal.config.get("filters")
		if not fl:
			return dest # Filters not enabled/configured

		name = dest.split("/")[0]

		ib = fl.get("inbound", {})
		ob = fl.get("outbound", {})

		ret = "/".join(ib.get(name, []) + [dest])
		ret = "/".join(ob.get(self.name, []) + [ret])

		return ret

	def raw_send(self, msg):
		if not msg.target:
			self.log.warning("Message passed to send without target")
			raise MalformedMsgException("raw_send given empty target")
		if not msg.origin:
			self.log.warning("Message passed to send without origin")
			raise MalformedMsgException("raw_send given empty origin")

		name = msg.target.split("/")[0]
		to = self._hal.objects.get(name)
		if to:
			nmsg = copy.copy(msg)
			return to._queue_msg(nmsg)
		else:
			self.log.warning("Unknown module/agent: " + name)


	def send_to(self, msg, dests):
		# Set origin for those who have not set it manually
		if msg.origin == None:
			msg.origin = self.name

		ret = {}
		for ri in dests:
			msg.target = self.apply_filter(ri)
			ret[ri] = self.raw_send(msg)

		return ret

	def sync_send_to(self, msg, dests):
		# Check for potential deadlocks
		for ri in dests:
			if ri.split('/')[0] == self.name:
				raise SyncSendSelfException

		msg.sync = True

		futs = self.send_to(msg, dests)

		r = {}
		for name, fut in futs.items():
			fut.result()
			to = self._hal.objects.get(name)
			if to and msg.uuid in to.sync_replies:
				# Assure that the module was not removed in the interim
				r[name] = to.sync_replies.pop(msg.uuid)
		return r

	async def _receive(self, msg):
		try:
			fname = 'receive_' + msg.type
			if hasattr(self, fname) and callable(getattr(self, fname)):
				# Type specific receive function
				getattr(self, fname)(msg)
			else:
				# Generic receive function
				self.receive(msg)
		except Exception as e:
			self.log.error("Exception in message receive", exc_info=True)

	def receive(self, msg):
		pass

	def receive_help(self, msg):
		if hasattr(self, 'topics'):
			if msg.body == []:
				# Retrieve available topics
				self.reply(msg, body=list(self.topics.keys()))
			else:
				# Retrieve help text for topic
				key = '/'.join(msg.body)
				if key in self.topics:
					t = self.topics[key]
					self.reply(msg, body=t() if callable(t) else t)

	class Configurer(HalConfigurer):
		pass

	# Configures an instance of this class based on the 'options' attribute
	@classmethod
	def configure(cls, conf, name=None):
		if name == None:
			name = input('Enter instance name: ')

		configurer = cls.Configurer(options=conf)
		configurer.configure()

		return name, configurer.options

	def invoke(self, inst, method, *args, **kwargs):
		return getattr(self._hal.objects[inst], method)(*args, **kwargs)
