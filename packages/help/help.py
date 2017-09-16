from halibot import HalModule

class Help(HalModule):

	def init(self):
		self.commands = {
			"help": self.help_
		}

	def receive(self, msg):
		if not msg.body or not msg.body.startswith("!"):
			return
		body = msg.body.split(" ")
		func = self.commands.get(body[0][1:])
		if func:
			func(body[1:], msg=msg)

	def help_(self, ls, msg=None):
		if not ls:
			resp = self.help()
		elif ls[0] not in [o[0] for o in self._hal.objects.items() if hasattr(o[1], "help")]:
			self.reply(msg, body="Topic '{}' not found!".format(ls[0]))
			return
		else:
			resp = self.invoke(ls[0], "help", args=" ".join(ls[1:]))

		# TODO: Let the agent handle this
		for r in resp.split("\n"):
			self.reply(msg, body=r)

	def help(self, args=""):
		if args == "!help":
			return ":)"
		# Allow admins to configure the greeting on the bot
		ret = self.config.get("banner", "Your friendly saltwater bot!")
		ret += " Use !help <topic> to get specific module help\n"
		# TODO: This should probably limit itself when there are too many objects
		# TODO: This should also be container-aware, so it should only report objects accessible from sender's RI
		# Only show modules that define a `.help()` method
		ret += "Loaded topics: " + ", ".join([o[0] for o in self._hal.objects.items() if hasattr(o[1], "help")])
		return ret
