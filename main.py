#!/usr/bin/env python3

import halibot
import json
import logging
import sys
import os

noGit = False
try:
	from git import Repo
except ImportError:
	noGit = True

# Defining the Halibot instance in global space so running with -i
#  makes it interactive
bot = None

def h_help(*args):
	print(
'''
Halibot - The world's greatest saltwater chat bot!

Commands:
	init    Initialize a new local halibot instance
	run     Run the local halibot instance
	fetch   Fetch remote packages by name
	help    Print this help text :)

''')
	sys.exit(0)

def h_init(*args):
	if not args:
		path = '.'
	else:
		path = args[0]

	if not os.path.exists(path):
		os.mkdir(path)
	else: # Dir does exist, ensure clear
		if os.listdir(path):
			r = input("Directory not empty, are you sure you want to init here? [y/N]: ")
			if not r.lower() in ("y", "yes", "yolo"):
				return

	if os.path.exists(os.path.join(path, "config.json")):
		r = input("A 'config.json' already exists, overwrite with new? [y/N]: ")
		if not r.lower() in ("y", "yes", "yolo"):
			return

	config = {
		"package-path": ["packages"],
		"repos": ["https://github.com/halibot-extra/"],
		"agent-instances": {},
		"module-instances": {}
	}

	with open(os.path.join(path,"config.json"),"w") as f:
		f.write(json.dumps(config, sort_keys=True, indent=4))

	if not os.path.exists("packages"):
		os.mkdir(os.path.join("packages"))
		print("Created '{}'".format(os.path.join(path,"packages")))

	print("Halibot instance has been initialized!")
	print("\nUse '{} run' to run the instance, or edit 'config.json' to add module/agent instances")

def h_run(*args):
	global bot
	# Maybe do the config loading here?
	if not os.path.exists("config.json"):
		print("Failed to start: No halibot configuration found in the current directory!")
		return

	logging.basicConfig(level=logging.DEBUG)
	bot = halibot.Halibot()
	bot.start(block=True)

def h_fetch(*args):
	# In order to access the config easily
	bot = halibot.Halibot()
	bot._load_config()

	# Error checking
	if noGit:
		print("The git python module is not installed, I cannot clone git repos.")
		return

	if not args:
		print("As you have asked me to fetch nothing, I shall fetch nothing.")
		return

	if not "repos" in bot.config:
		print("There are no repos specified in the config.json.")
		print("I have nothing to fetch from!")
		return

	# Try to fetch each requested package
	for name in args:
		# Install to the first package path by default
		dst = os.path.join(bot.config["package-path"][0], name)

		success = False
		for r in bot.config["repos"]:
			src = r + name
			try:
				print("Trying to git clone '{}'...".format(src))
				Repo.clone_from(src, dst)
				print("\033[92mSuccessfully fetched '{}' into '{}'.\033[0m".format(name, dst))
				success = True
				break
			except Exception as e:
				print(e)

		if not success:
			print("\033[91mFailed to fetch '{}'!\033[0m".format(name))


arg_map = {
	"help": h_help,
	"init": h_init,
	"run": h_run,
	"fetch": h_fetch
}

# TODO: Rewrite this with argparse or something

if len(sys.argv) > 1 and sys.argv[1] in arg_map:
	arg_map.get(sys.argv[1])(*sys.argv[2:])
else:
	h_help()
