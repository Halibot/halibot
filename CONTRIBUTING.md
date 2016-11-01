We are generally lax in accepting changes.
Changes should be submitted as either a pull request on GitHub, or contact us on Freenode in `##halibot` with a `git format-patch`'d patch file.
We may request alterations to your pull request if we deem it malapropos or inelequent.

Things that will cause your pull request to be rejected (but not limited to):
 - Using spaces instead of tabs
 - Large commits. Please break up changes into multiple single-purpose commits
 - Lack of, or inadequate commit messages

Things we prefer in pull requests:
 - Loosely adhereing to the kernel-style commits (see example below)

Example commit message format:

```
(object or concept changed): (imperative-tone short description of change)

(Long description including motivation goes here)

---

halibot: add ability to reload a module

Once a module is loaded and initialized, changing the module's files on disk
will not reflect in the running instance. It is useful to be able to restart
and update modules on the fly, without having to restart the whole halibot
instance.

This commit introduces a reload_module() function to Halibot core to facilate
a complete restart and reload of a particular module.

```

While we won't necessarily reject a pull request completely based on the commit message, it is preferred to use a format similar to this.
If it is difficult to describe the change in one line, or, if the commit changes too many different things, it may be a hint that the commit should be broken up further.
