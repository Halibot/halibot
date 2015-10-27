# Halibot [![Build Status](https://travis-ci.org/Halibot/halibot.svg)](https://travis-ci.org/Halibot/halibot)
The world's greatest saltwater multi-protocol chat bot framework!

For the module and agent repositories, see [halibot-extra](https://github.com/halibot-extra).

This is the repository for the new rewrite (codename halv3). For the old XMPP-specific version which this is mostly based on, please see [halibot/halibot-legacy](http://github.com/halibot/halibot-legacy).

Check out our [sweet site](https://halibot.github.io)!

## Usage

In order to run halibot, you need a config file by the name of `config.json`. As of now, this file should be located in the root project directory (Alongside this README).

Here is an example config for reference:

```json
{
  "module-path": [
    "modules"
  ],

  "agent-path": [
    "agents"
  ],

  "agent-instances": {
    "irc0": {
      "of": "irc",
      "channel": "##example",
      "nickname": "ExampleName"
    }
  },

  "module-instances": {
    "hello0": {
      "of": "hello"
    }
  }
}
```
