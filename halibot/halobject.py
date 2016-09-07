import logging
import asyncio
import inspect
from threading import Thread

class HalObject():

	def __init__(self, hal, conf={}):
		self._hal = hal
		self.config = conf
		self.log = logging.getLogger(self.__class__.__name__) # TODO: Put instantiated name in here too

		self.eventloop = asyncio.SelectorEventLoop()
		self._thread = Thread(target=self.eventloop.run_forever)
		self._thread.start()

	def _shutdown(self):
		self.eventloop.call_soon_threadsafe(self.eventloop.stop)
		self._thread.join()
		self.shutdown()

	def _queue_msg(self, msg, whom):
		self.eventloop.call_soon_threadsafe(self._receive, msg, whom)

	# Calls receive() with the proper number of arguments
	def _receive(self, msg, whom):
		if len(inspect.getargspec(self.receive).args) == 2:
			self.receive(msg)
		else:
			self.receive(msg, whom)

	def init(self):
		pass

	def shutdown(self):
		pass

	def send_to(self, msg, dests):
		for ri in dests:
			name = ri.split('/')[0]
			whom = '/'.join(ri.split('/')[1:])
			to = self._hal.get_object(name)
			if to:
				to._queue_msg(msg, whom)
			else:
				self.log.warning('Unknown module/agent: ' + str(name))

	def receive(self, msg, whom):
		self.log.debug("Received from base: " + str(msg))
		pass

