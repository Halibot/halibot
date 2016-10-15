# Halibot [![Build Status](https://travis-ci.org/Halibot/halibot.svg)](https://travis-ci.org/Halibot/halibot)
The world's greatest saltwater multi-protocol chat bot framework!

For the module and agent repositories, see [halibot-extra](https://github.com/halibot-extra).

This is the repository for the new rewrite (codename halv3). For the old XMPP-specific version which this is mostly based on, please see [halibot/halibot-legacy](http://github.com/halibot/halibot-legacy).

You can contact us in ##halibot on freenode. If you wait around for long enough you will get a response!

Check out our [sweet site](https://halibot.github.io)!

## Installation

Currently, Halibot is only available from this repo.

```
git clone https://github.com/halibot/halibot
cd halibot
./install.sh
```

Extra packages are available at `https://github.com/halibot-extra`.

## Basic Usage

In order for Halibot to run, you need a config.json (see the next section(s) for an example config and explanation).

To create a default config, you can execute:

```
halibot init
```

To actually run the bot, you can execute:
```
halibot run

# If you want an interactive python REPL to play with the bot:
halibot run -i
```

## Configuration

Halibot needs a valid configuration to run named `config.json`.
The following subsections will provide an example config, and a line-by-line explanation of each option.
Halibot uses valid python JSON, and will throw errors if the `config.json` does not conform to the strict JSON specification.

### Example Config

```json
{
  "package-path": [
    "packages"
  ],

  "agent-instances": {
    "irc0": {
      "of": "irc:IrcAgent",
      "channel": "##example",
      "nickname": "ExampleName"
    }
  },

  "module-instances": {
    "hello0": {
      "of": "hello:Hello"
    }
  }
}
```

### Packages

A halibot *package* is, simply put, a collection of code.
Each package can contain a collection of module and agent classes, which can be instatied inside the `module-instances` and `agent-instances` section of the config.

The `package-path` key is a list of path strings informing halibot where to look for packages.

In the above example, the single directory `packages` is used.
This path is relative to where Halibot is being run from.
Alternatively, you could specify the absolute path `/usr/lib/halibot/modules`.

Halibot ships with an example IRC agent, and an example "Hello world!" module, so if you run Halibot from the installation (repo) directory, the above config should be valid.

Jump to the section titled **Modules and Agents** below for more information on how these function in the larger Halibot system.

### `agent-instances` and `module-instances`

Agents and modules need to be instantiated before they can be used.
Each instance has its own name and configuration -- this means there can be multiple agents and modules of the same type.
Specifying this deviates a bit from what might be considered "normal" JSON.
The `agent-instances` and `module-instances` keys each are mapped to an object, whose keys are the **names** of the relevant Halibot objects.
So, in the above example in `agent-instances`, we mapped the following:

```json
"irc0": {
  "of": "irc:IrcAgent",
  "channel": "##example",
  "nickname": "ExampleName"
}
```

Here, `irc0` is the name, and the object is its configuration.
Agents and modules may specify what configuration is required, but **ALL** objects need and `of` key, which refers to *what* it actually is.
The component of the `of` field before the colon (`:`) specifies the name of the package in which the class the instance is of is located in,
while the component after the colon is the python name of the class within that package.

Modules operate in the same sense.

#### Per-agent/module configuration

Some modules/agents may require certain key-value pairs to be defined to operate correctly.
For example, an `irc:IrcAgent` agent needs a `nickname` string, to use for connection.
This is only for this particular agent instance, so in theory, another instance could be spun up with a different name, and specify a different nickname.

These keys are module/agent specific, so see the individual documentation for a package on what fields are allowed.
