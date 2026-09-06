# Zeppelin Embed Homebrew Tap

Official Homebrew formulae for [Zeppelin Embed](https://github.com/zepdb/zeppelin-embed), the in-process vector, lexical, and hybrid search engine for macOS and Apple silicon.

Install the language-neutral C SDK with:

```sh
brew install zepdb/tap/zeppelin-embed
```

The formula installs the public C header plus static and dynamic libraries. Language packages such as Rust, Python, Swift, and Node.js are distributed through their native package managers.

The tap checks for new published releases every hour. It verifies the SDK archive layout and pins each formula to the release asset's SHA-256 checksum before updating `main`.
