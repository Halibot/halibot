from .halobject import HalObject

class HalAgent(HalObject):

	def dispatch(self, msg):
		out = self.config.get('out', self._hal.objects.modules.keys())
		self.send_to(msg, out)

	def connect(self, to):
		# FIXME Don't modify the config like this?
		if 'out' in self.config:
			self.config['out'].append(to.name)
		else:
			self.config['out'] = [ to.name ]

