from halmodule import HalModule

class Hello(HalModule):

	def init(self):
		pass

	def receive(self, msg):
		if msg["body"].startswith("!hello"):
			self.reply(msg, body="Hello world!")

