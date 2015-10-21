import logging
import asyncio
from threading import Thread

class HalObject():

	def __init__(self, hal, conf):
		self._hal = hal
		self.config = conf
		self.log = logging.getLogger(self.__class__.__name__) # TODO: Put instantiated name in here too

		self.eventloop = asyncio.SelectorEventLoop()
		self._thread = Thread(target=self.eventloop.run_forever)
		self._thread.start()

	def _queue_msg(self, msg):
		self.eventloop.call_soon_threadsafe(self.receive, msg.copy())

	def init(self):
		pass

	def shutdown(self):
		self.eventloop.call_soon_threadsafe(self.eventloop.stop)
		self._thread.join()

	# See halmodule and halagent for their respective implementations
	def send(self, msg):
		pass

	def send_to(self, msg, dests):
		for name in dests:
			to = self._hal.get_object(name)
			if to:
				to._queue_msg(msg)
			else:
				self.log.warning('Unknown module/agent: ' + str(name))

	def receive(self, msg):
		self.log.debug("Received from base: " + str(msg))
		pass

