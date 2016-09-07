from halibot import HalAgent

class AgentContainer(HalAgent):

	def receive(self, msg, whom):
		suff = '/' + whom if whom != '' else ''
		cont = self.config.get('contents', [])
		self.send_to(msg, [ name + suff for name in cont ])

