# loqet
Loqet is a local python secret manager. The Loqet package comes with two primary tools: `loq` and `loqet`.

`loq` is a standalone file encryption tool. Encrypt, decrypt, read, edit, search, and diff `loq` encrypted files.

`loqet` is a context-managed secret store. Create a `loqet context` for each of your projects, and store your project secrets, encrypted at rest. Use the `loqet` command line tool to interact with your encrypted secret store, and use the `loqet` python API to read your encrypted secrets at runtime.

---

## How to install
```shell
pip install loqet
```

---

## Loq or Loqet, which should I use?
`loq` is great for encrypting single files that stand alone and don't need programmatic access. Lock up some passwords, bank account info, or crypto seed phrases to look at later when you need them. Alternatively, if you (securely) give a friend a loq key, you can send each other secret messages. I'll leave that up to you to figure out.

`loqet` is great for projects with secrets in their configs, or when you have groups of many secrets. It's also great for secret management in a project shared between multiple contributors, since you can securely share the keyfile, and commit encrypted secrets to a shared version control system.

---

## Docs
* [loq command line interface](docs/loq_cli.md)
* [loqet command line interface](docs/loqet_cli.md)
* [loqet python API](docs/loqet_api.md)
* [loq/loqet configs](docs/configs.md)
