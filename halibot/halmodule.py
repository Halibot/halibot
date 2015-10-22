from .halobject import HalObject

class HalModule(HalObject):

	def send(self, msg):
		out = self.config.get('out', [ msg['context']['agent'] ])
		self.send_to(msg, out)

