import logging
from .jsdict import jsdict

# Deprecated, remove at 1.0
class Context():
	
	def __init__(self, **kwargs):
		self.agent = kwargs.get('agent', None)
		self.protocol = kwargs.get('protocol', None)
		self.whom = kwargs.get('whom', None)

	def __setattr__(self, key, value):
		object.__setattr__(self, key, value)

		if 'message' in dir(self):
			self.message.log.warning('Deprecated use of "context" field on Message object')
			object.__setattr__(self.message, 'origin', self.makeOrigin())

	def makeOrigin(self):
		if self.agent == None:
			return None
		o = self.agent
		if self.whom != None:
			o += '/' + self.whom
		return o

class Message():

	def __init__(self, **kwargs):
		self.log = logging.getLogger(self.__class__.__name__)

		self.body = kwargs.get('body', None)
		self.type = kwargs.get('type', 'simple')
		self.author = kwargs.get('author', None)
		self.identity = kwargs.get('identity', None)
		self.origin = kwargs.get('origin', None)
		self.misc = kwargs.get('misc', jsdict())
		self.target = kwargs.get('target', '')

		# Deprecated, remove at 1.0
		# Supresses expected warning message
		object.__setattr__(self, 'context', kwargs.get('context', Context()))
		object.__setattr__(self.context, 'message', self)

		if not 'origin' in kwargs:
			object.__setattr__(self, 'origin', self.context.makeOrigin())
		else:
			# to setup the context properly
			self.origin = self.origin

	# Deprecated, remove at 1.0
	def __setattr__(self, key, value):
		if key == 'context':
			self.log.warning('Deprecated use of "context" field on Message object')
			value.message = self
			object.__setattr__(self, 'origin', value.makeOrigin())

		if key == 'origin' and value != None and 'context' in dir(self):
			ls = value.split('/')
			object.__setattr__(self.context, 'agent', ls[0])
			object.__setattr__(self.context, 'whom', '/'.join(ls[1:]))

		object.__setattr__(self, key, value)

	def whom(self):
		return '/'.join(self.target.split('/')[1:])
