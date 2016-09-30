from halibot import HalAgent

class AgentContainer(HalAgent):

	def receive(self, msg):
		self.send_to(msg, self.config.get('contents', []))

