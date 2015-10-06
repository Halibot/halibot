class HalModule():
	
	_hal = None

	def __init__(self, hal, conf):
		self._hal = hal
		self.config = conf

	def init(self):
		pass

	def send(self, msg0):
		msg = msg0.copy()
		msg["source"] = "module"
		self._hal.receive(msg)

	def receive(self, msg):
		pass

	def reply(self, msg0, body=""):
		# this does a double copy :(
		msg = msg0.copy()
		msg["body"] = body

		self.send(msg)
