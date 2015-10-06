class HalAgent():
	
	_hal = None

	def __init__(self, hal, conf):
		self._hal = hal
		self.config = conf

	def init(self):
		pass

	def send(self, msg0):
		msg = msg0.copy()
		msg["source"] = "agent"
		self._hal.receive(msg)

	def receive(self, msg):
		pass
