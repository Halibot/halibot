from halobject import HalObject

class HalModule(HalObject):

	def send(self, msg):
		out = self.config.get('out', [ msg['context']['agent'] ])

		for name in out:
			to = self._hal.get_object(name)
			if to:
				to._queue_msg(msg)
			else:
				self.log.warning('Unknown module/agent: ' + str(name))
