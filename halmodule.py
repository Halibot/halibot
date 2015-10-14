import logging

class HalModule():
	
	_hal = None
	log = None

	def __init__(self, hal, conf):
		self._hal = hal
		self.config = conf
		self.log = logging.getLogger(self.__class__.__name__) # TODO: Put instantiated name in here too

	def init(self):
		pass

	def send(self, msg0):
		self.log.debug("Sending to base: " + str(msg0))
		msg = msg0.copy()
		msg["source"] = "module"
		self._hal.receive(msg)

	def receive(self, msg):
		self.log.debug("Received from base: " + str(msg0))

	def reply(self, msg0, body=""):
		# this does a double copy :(
		msg = msg0.copy()
		msg["body"] = body

		self.send(msg)
