class HalModule():
	
	_hal = None

	def __init__(self, hal, conf):
		self._hal = hal
		self.config = conf

	def init(self):
		pass

	def send(self, msg):
		msg["source"] = "module"
		self._hal.receive(msg)

	def receive(self, msg):
		pass

	def reply(self, msg, body=""):
		msg["body"] = body

		self.send(msg)
