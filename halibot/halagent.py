from .halobject import HalObject

class HalAgent(HalObject):

	def dispatch(self, msg):
		# TODO: Force set origin first, or should we assume it is set?
		self.send_to(msg, self._hal.routing.get(msg.origin))
