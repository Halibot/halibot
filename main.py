#!/usr/bin/env python3

import halibot
import imp
import logging

# Reloads the halibot core, does not reinitialize modules/agents
#  Takes in old bot instances, returns new bot
def hal_reload(bot):
	global halibot
	halibot = imp.reload(halibot)

	newbot = halibot.Halibot()

	newbot.config = bot.config
	newbot.agents = bot.agents
	newbot.modules = bot.modules
	newbot.queue = bot.queue

	newbot.running = True
	newbot._start_route()
	return newbot

def main():
	logging.basicConfig(level=logging.DEBUG)
	bot = halibot.Halibot()
	bot.start(block=True)

	# Keeps reloading halibot if rld is set to True
	while True:
		while bot.running:
			pass

		# Put this is a deinit?
		bot.thread.join()

		if bot.rld:
			bot = hal_reload(bot)
		else:
			break

if __name__ == "__main__":
	main()
