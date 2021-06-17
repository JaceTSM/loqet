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

## Getting Started
For more detailed docs, please see the links at the bottom of the page.

`loq`:
```shell
# Create loq secret key for loq CLI to use (default: ~/.loqet/loq.key)
loq init

# Encrypt/Decrypt and Interact with encrypted files
loq encrypt myfile.yaml
loq edit myfile.yaml.loq
loq view myfile.yaml.loq
loq decrypt myfile.yaml.loq
```

`loqet`:
```shell
# Create loqet context named "myproject", and set it as the active context
# Default configuration found at ~/.loqet/contexts.yaml
loqet context init myproject /path/to/myproject/secret_dir
loqet context set myproject

loqet create passwords      # creates "passwords" loqet namespace
loqet edit passwords        # fill in contents to the password loqet's .loq file (encrypted)
loqet view passwords --loq  # shows your edits in the loq file
loqet decrypt passwords     # writes your decrypted edits to the password loqet's .open file 
loqet get passwords.path.to.value   # reads a value from your loqet
```

`loqet` python api:
```python
import loqet

my_username = loqet.loqet_get("passwords.mysql.users.0.username")  # sample secret namespace path
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
