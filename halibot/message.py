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

	def __repr__(self):
		return "halibot.Message(body='{}', type='{}', author='{}', identity='{}', origin='{}', misc='{}', target='{}')".format(self.body, self.type, self.author, self.identity, self.origin, self.misc, self.target)

	def __str__(self):
		return "body='{}' type='{}' author='{}' origin='{}' target='{}'".format(self.body, self.type, self.author, self.origin, self.target)
