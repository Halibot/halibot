from halmodule import HalModule

class Quote(HalModule):

	def init(self):
		pass

	def receive(self, msg):
		if msg["body"].startswith("!quote"):
			self.reply(msg, body="Hello world!")

