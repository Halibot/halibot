#
# CommandModule
#    Subclass of HalModule that does the heavy lifting of commands for you
#
from . import HalModule
from enum import Enum, auto

class Reason(Enum):
	NO_PREFIX = auto()
	BAD_NAMESPACE = auto()
	NAMESPACE_ONLY = auto()
	UNKNOWN_COMMAND = auto()

# Decorator for converting the string stripped of the command to an argument list
def AsArgs(func):
	def wrapper(self, string, msg=None):
		args = string.split(" ")
		func(self, args, msg=msg)
	return wrapper

class CommandModule(HalModule):

	# Subclasses should implement a commands table like the following.
	#   Note, the "values" should be methods on the CommandModule-derived class
	#   Forgoing this is inadvisable (e.g. loss of _hal reference)
	#     "command" -> func(self, string, msg=msg)
	#   string: by default, will be the message not split into arguments
	#     use the annotation AsArgs above to override this
	#   msg: not needed in all commands, the message object as received

	def __init__(self, hal, conf={}):
		super().__init__(hal, conf=conf)

		self.commands = {}
		# Get the command prefix if defined, otherwise use "!" as default
		self.prefix = self._hal.config.get("command_prefix", "!")
		self.namespace = None

	# Override only if you know what you are doing!
	def receive(self, msg):
		self._cmd_receive(msg)

	# Actually does the command handling logic. Separate callable so multi-inheritance
	#  can work nicely (maybe)
	def _cmd_parse(self, msg):
		body = msg.body.split(" ", 1)
		if body and not body[0].startswith(self.prefix):
			return Reason.NO_PREFIX
		body[0] = body[0][1:]

		if self.namespace:
			name = body.pop(0)

			if name != self.namespace:
				return Reason.BAD_NAMESPACE
			if len(body) == 0:
				return Reason.NAMESPACE_ONLY

		# Ugly fix for commands without args
		if len(body) == 1:
			body.append("")

		# This maybe should prevent a empty string as a key...
		func = self.commands.get(body[0])

		if func:
			func(body[1], msg=msg)
		else:
			return Reason.UNKNOWN_COMMAND

	def _cmd_receive(self, msg):
		reason = self._cmd_parse(msg)
		if reason:
			self.default(msg, reason=reason)


	# Override this to provide some functionality if there is no match in the table
	def default(self, msg, reason=None):
		pass
