from halibot import CommandModule
from halibot.halauth import hasPermission

class PermissionManager(CommandModule):
	def init(self):
		self.commands = {
			"grant":  self.grant_,
			"revoke": self.revoke_,
		}

	@hasPermission("PERM_GRANT", reply=True)
	def grant_(self, argv, msg=None):
		try:
			ri, identity, perm = argv.split(" ")
		except:
			self.reply(msg, body="Must be in the form '<ri> <identity> <perm>'")
			return

		if self._hal.auth.grantPermission(ri, identity, perm):
			self._hal.auth.write_perms()

	@hasPermission("PERM_REVOKE", reply=True)
	def revoke_(self, argv, msg=None):
		try:
			ri, identity, perm = argv.split(" ")
		except:
			self.reply(msg, body="Must be in the form '<ri> <identity> <perm>'")
			return

		if self._hal.auth.revokePermission(ri, identity, perm):
			self._hal.auth.write_perms()
