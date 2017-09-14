import logging
import uuid
from .jsdict import jsdict

class Message():

	def __init__(self, **kwargs):
		self.log = logging.getLogger(self.__class__.__name__)
		self.uuid = uuid.uuid4()
		self.sync = False

		self.body = kwargs.get('body', None)
		self.type = kwargs.get('type', 'simple')
		self.author = kwargs.get('author', None)
		self.identity = kwargs.get('identity', None)
		self.origin = kwargs.get('origin', None)
		self.misc = kwargs.get('misc', jsdict())
		self.target = kwargs.get('target', '')

	def whom(self):
		return '/'.join(self.target.split('/')[1:])
