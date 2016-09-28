from .halobject import HalObject
from .message import Message

class HalModule(HalObject):

	def reply(self, msg0=None, **kwargs):
		body = kwargs.get('body', msg0.body)
		mtype = kwargs.get('type', msg0.type)
		author = kwargs.get('author', msg0.author)
		origin = kwargs.get('origin', msg0.origin)

		msg = Message(body=body, type=mtype, author=author, origin=origin)

		# For deprecation, remove for 1.0
		if 'context' in kwargs:
			msg.context = kwargs['context']

		self.send_to(msg, [ msg.origin ])

	def hasPermission(self, msg, perm):
		return self._hal.auth.hasPermission(msg.origin, msg.author, perm)
