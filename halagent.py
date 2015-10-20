from halobject import HalObject

class HalAgent(HalObject):

	def send(self, msg):
		out = self.config.get('out', self._hal.modules.keys())

		for name in out:
			to = self._hal.get_object(name)
			if to:
				to._queue_msg(msg)
			else:
				self.log.warning('Unknown module/agent: ' + str(name))

