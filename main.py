#!/usr/bin/env python3

import halibot
import imp
import logging

def main():
	logging.basicConfig(level=logging.DEBUG)
	bot = halibot.Halibot()
	bot.start(block=True)

if __name__ == "__main__":
	main()
