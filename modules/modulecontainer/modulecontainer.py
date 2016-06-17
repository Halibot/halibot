from halibot import HalModule

class ModuleContainer(HalModule):

	def receive(self, msg):
		self.send_to(msg, self.config.get('contents', []))

