import logging
import asyncio
import inspect
import copy
from threading import Thread
from collections import defaultdict
from .halconfigurer import HalConfigurer

class HalObject():

	def __init__(self, hal, conf={}):
		self._hal = hal
		self.config = conf
		self.log = logging.getLogger(self.__class__.__name__) # TODO: Put instantiated name in here too

		# Only used in HalModule.reply right now, but accessed on potentially any
		# HalObject, so it exists on every HalObject to avoid attribute errors
		self.sync_replies = defaultdict(lambda: []) # UUID -> [Message, ...]

		self.eventloop = asyncio.SelectorEventLoop()
		self._thread = Thread(target=self.eventloop.run_forever)
		self._thread.start()

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

	def send_to(self, msg, dests):
		# Set origin for those who have not set it manually
		if msg.origin == None:
			msg.origin = self.name

		ret = {}
		for ri in dests:
			name = ri.split('/')[0]
			to = self._hal.objects.get(name)
			if to:
				nmsg = copy.copy(msg)
				nmsg.target = ri
				ret[ri] = to._queue_msg(nmsg)
			else:
				self.log.warning('Unknown module/agent: ' + str(name))
		return ret

	def sync_send_to(self, msg, dests):
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
		self.receive(msg)


	def receive(self, msg):
		pass


	class Configurer(HalConfigurer):
		pass

	# Configures an instance of this class based on the 'options' attribute
	@classmethod
	def configure(cls, conf):
		name = input('Enter instance name: ')

		configurer = cls.Configurer()
		configurer.configure()

		conf = {**conf, **configurer.options}

		return name, conf

	def invoke(self, inst, method, *args, **kwargs):
		return getattr(self._hal.objects[inst], method)(*args, **kwargs)
