from .halobject import HalObject

class HalAgent(HalObject):

	def send(self, msg):
		out = self.config.get('out', self._hal.modules.keys())
		self.send_to(msg, out)

