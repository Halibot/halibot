import logging
from queue import Queue
from threading import Thread

class HalObject():

	def __init__(self, hal, conf):
		self._hal = hal
		self.config = conf
		self.log = logging.getLogger(self.__class__.__name__) # TODO: Put instantiated name in here too

		self._msg_queue = Queue()
		self._thread = Thread(target=self._spin)
		self._thread.start()

	def _spin(self):
		while True:
			m = self._msg_queue.get()
			self.receive(m)
			self._msg_queue.task_done()

	def _queue_msg(self, msg):
		self._msg_queue.put(msg.copy())

	def init(self):
		pass

	# See halmodule and halagent for their respective implementations
	def send(self, msg):
		pass

	def receive(self, msg):
		self.log.debug("Received from base: " + str(msg))
		pass

