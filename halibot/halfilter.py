from .halobject import HalObject

class HalFilter(HalObject):

	# Override this in subclasses to determine filter logic
	#  Return None to reject message
	#  Otherwise, return the message object with any modifications necessary
	def filter(self, msg):
		return msg

	def receive(self, msg):
		try:
			# Trim off this filter's target
			msg.target = msg.target.split("/",1)[1]
		except:
			# This shouldn't happen with a proper RI
			self.log.error("Target RI cannot be split, did someone send this filter a message directly?")
			return

		msg = self.filter(msg)
		if msg:
			self.raw_send(msg)
