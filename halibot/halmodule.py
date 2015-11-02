from .halobject import HalObject
from .message import Message

class HalModule(HalObject):

	def reply(self, msg0=None, **kwargs):
		body = kwargs.get('body', msg0.body)
		mtype = kwargs.get('type', msg0.type)
		author = kwargs.get('author', msg0.author)
		context = kwargs.get('context', msg0.context)

		msg = Message(body=body, type=mtype, author=author, context=context)

		self.send_to(msg, [ msg.context.agent ])

