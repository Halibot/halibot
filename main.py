#!/usr/bin/env python3

import halibot
import json
import logging
import sys
import os

# Defining the Halibot instance in global space so running with -i
#  makes it interactive
bot = None

def h_help(*args):
	print(
'''
Halibot - The world's greatest saltwater chat bot!

Commands:
	init	Initialize a new local halibot instance
	run	Run the local halibot instance
	help	Print this help text :)

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

	# NOTE: Update for packages
	if not os.path.exists("modules"):
		os.mkdir(os.path.join("modules"))
		print("Created '{}'".format(os.path.join(path,"modules")))
	if not os.path.exists("agents"):
		os.mkdir(os.path.join("agents"))
		print("Created '{}'".format(os.path.join(path,"agents")))

	if os.path.exists(os.path.join(path, "config.json")):
		r = input("A 'config.json' already exists, overwrite with new? [y/N]: ")
		if not r.lower() in ("y", "yes", "yolo"):
			return

	config = {
		"agent-path": ["agents"],
		"module-path": ["modules"],
		"agent-instances": {},
		"module-instances": {}
	}

	with open(os.path.join(path,"config.json"),"w") as f:
		f.write(json.dumps(config, sort_keys=True, indent=4))

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

arg_map = {
	"help": h_help,
	"init": h_init,
	"run": h_run,
}

# TODO: Rewrite this with argparse or something

if len(sys.argv) > 1 and sys.argv[1] in arg_map:
	arg_map.get(sys.argv[1])(*sys.argv[2:])
else:
	h_help()
