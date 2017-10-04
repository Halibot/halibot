#
# HelpModule
#
from halibot import CommandModule, Message

class Help(CommandModule):

	def init(self):
		self.commands = {
			'help' : self.command
		}

	def general_help(self, target):
		hmsg = Message(body=[], type='help', origin=self.name)
		replies = self.sync_send_to(hmsg, target)

		text = '''The help command gives useful help messages.

Syntax:
  !help <topic> [<subtopic> ...]

Available topics:
'''
		# Collect the available topics
		topics = []
		for r in replies.values():
			topics += [t for t in r[0].body if not t in topics]

		# Append the available topics to the list
		c = 2
		line = '  '
		max_column = 80
		first = True
		for t in topics:
			if c + len(t) + 2 > max_column:
				text += line + '\n'
				c = 2
				line = '  '
				first = True

			if first:
				first = False
			else:
				line += ', '
				c += 2

			line += t
			c += len(t)

		# Append final line
		if line.strip() != '':
			text += line + '\n'

		return text

	def command(self, args, msg=None):
		# TODO When containers/routes become more integrated, just look at the
		#      container the message was sent to, which shoudl work for the
		#      default container as well.
		target = self.config.get('target', self._hal.objects.modules.keys())
		target = [t for t in target if t.split('/')[0] != self.name] # Can't sync send to this module

		if args == '':
			self.reply(msg, body=self.general_help(target))
		else:
			hmsg = Message(body=args.split(' '), type='help', origin=self.name)
			replies = self.sync_send_to(hmsg, target)

			if len(replies) > 0:
				# TODO check for discrepancies among replies
				self.reply(msg, body=list(replies.values())[0][0].body)
