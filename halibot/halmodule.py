from .halobject import HalObject
from .message import Message

class HalModule(HalObject):

	def reply(self, msg0=None, **kwargs):
		# Create the reply message
		body = kwargs.get('body', msg0.body)
		mtype = kwargs.get('type', msg0.type)
		author = kwargs.get('author', msg0.author)
		origin = kwargs.get('origin', msg0.origin)

		msg = Message(body=body, type=mtype, author=author, origin=origin)

		# Synchronous reply?
		if msg0.sync:
			self.sync_replies[msg0.uuid].append(msg)
		else:
			self.send_to(msg, [ msg.origin ])

	def hasPermission(self, msg, perm):
		return self._hal.auth.hasPermission(msg.origin, msg.identity, perm)
