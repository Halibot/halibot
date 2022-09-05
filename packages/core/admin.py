#
# Admin control module
#  Basic commands to manage a running halibot instance from an agent
#
from halibot import CommandModule, Message
from halibot.halauth import hasPermission

class Admin(CommandModule):

	VERSION = "1.0.0"
	HAL_MINIMUM = "0.1"

	def init(self):
		self.commands = {
			"shutdown": self.cmd_shutdown,
			"reload": self.cmd_reload,
		}

	@hasPermission("ADMIN", reply=True, permissive=False)
	def cmd_shutdown(self, args, msg=None):
		self._hal.shutdown()

	@hasPermission("ADMIN", reply=True, permissive=False)
	def cmd_reload(self, args, msg=None):
		try:
			self._hal.reload(args)
		except Exception as e:
			self.reply(msg, body=f"Could not reload '{args}': {e}")
		else:
			self.reply(msg, body=f"Successfully reloaded '{args}'!")