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

	# See halmodule and halagent for their respective implementations
	def send(self, msg):
		pass

	def receive(self, msg):
		self.log.debug("Received from base: " + str(msg))
		pass

