# Halibot [![Build Status](https://travis-ci.org/Halibot/halibot.svg)](https://travis-ci.org/Halibot/halibot)
The world's greatest saltwater multi-protocol chat bot framework!

For the module and agent repositories, see [halibot-extra](https://github.com/halibot-extra).

This is the repository for the new rewrite (codename halv3). For the old XMPP-specific version which this is mostly based on, please see [halibot/halibot-legacy](http://github.com/halibot/halibot-legacy).

You can contact us in ##halibot on freenode. If you wait around for long enough you will get a response!

Check out our [sweet site](https://halibot.github.io)!

## Installation

Currently, Halibot is only available from this repo.

```
git clone http://www.github.com/halibot/halibot
```

## Basic Usage

In order for Halibot to run, you need a config.json (see the next section(s) for an example config and explanation).
From the installation directory (after the clone, `cd halibot`), execute any of the following:
```
# Should work in most cases
./main.py

# If the above fails:
python3 main.py

# If you want an interactive python REPL to play with the bot:
python3 -i main.py
```

## Configuration

Halibot needs a valid configuration to run named `config.json`.
The following subsections will provide an example config, and a line-by-line explanation of each option.
Halibot uses valid python JSON, and will throw errors if the `config.json` does not conform to the strict JSON specification.

### Example Config

```json
{

  "agent-path": [
    "agents"
  ],

  "module-path": [
    "modules"
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

### `agent-path` and `module-path`

The `module-path` and `agent-path` keys are an array of directories to look for modules or agents.
Simply put, these should be a list of strings pointing to where Halibot should look for the fun things.
In the above example, the directories `modules` and `agents` are used.
These are relative paths from where Halibot is being run.
Alternatively, you could specify `/usr/lib/halibot/modules`, and that would be an absolute path.

Essentially, these should be where you install the extra modules or agents.
Halibot ships with an example IRC agent, and an example "Hello world!" module, so if you run Halibot from the installation (repo) directory, the above paths should be valid.

Jump to the section titled **Modules and Agents** below for more information on how these function in the larger Halibot system.

### `agent-instances` and `module-instances`

Agents and modules need to be instantiated before they can be used.
Each instance has its own name and configuration -- this means there can be multiple agents and modules of the same type.
Specifying this deviates a bit from what might be considered "normal" JSON.
The `agent-instances` and `module-instances` keys each are mapped to an object, whose keys are the **names** of the relevant Halibot objects.
So, in the above example in `agent-instances`, we mapped the following:

```json
"irc0": {
  "of": "irc",
  "channel": "##example",
  "nickname": "ExampleName"
}
```

Here, `irc0` is the name, and the object is its configuration.
Agents and modules may specify what configuration is required, but **ALL** objects need and `of` key, which refers to *what* it actually is.
Again, in the above example, `irc0`'s `of` is `irc`.
This tells Halibot to use agent specified in the `irc` directory in `agent-path`. (in the above example, should be `./agents/irc`)

Modules operate in the same sense.
The `hello0` instance listed in the `module-instances` object refers to the module in the `./modules/hello` directory.

#### Per-agent/module configuration

Some modules/agents may require certain key-value pairs to be defined to operate correctly.
For example, an `irc` agent needs a `nickname` string, to use for connection.
This is only for this particular agent instance, so in theory, another instance could be spun up with a different name, and specify a different nickname.
