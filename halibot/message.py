from .jsdict import jsdict

class Context():
	
	def __init__(self, **kwargs):
		self.agent = kwargs.get('agent', None)
		self.protocol = kwargs.get('protocol', None)
		self.whom = kwargs.get('whom', None)

class Message():

	def __init__(self, **kwargs):
		self.body = kwargs.get('body', None)
		self.type = kwargs.get('type', 'simple')
		self.author = kwargs.get('author', None)
		self.context = kwargs.get('context', Context())
		self.misc = kwargs.get('misc', jsdict())

