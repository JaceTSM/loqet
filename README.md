# loqet
Local python secret manager

## How to install
pip install coming soon

---
# CLI Usage

## loq: encryption tool
`loq` is a command line encryption tool. It allows you to encrypt/decrypt files, view and edit encrypted files, diff encrypted files, and search through encrypted files. Files encrypted with the `loq` tool have the `.loq` extension. When you decrypt a `.loq` file, a `.open` file is created. This serves two functions:
1. If you encrypt, edit, then decrypt a file, you don't overwrite the original file contents.
2. If you are using git, You can add `*.open` to your `.gitignore`, preventing unencrypted secrets from being committed. (You will still need to manage the original, non-`.open` file, whether you delete it, gitignore it, or move it elsewhere is up to you)

To use the `loq` encryption tool, you must first set up a `loq key`, which will be used to encrypt and decrypt files when using the `loq` tool. You can generate a key with `loq init`. The key will be saved to `~/.loqet/loq.key` by default (env var `LOQ_KEY_FILE`).

`loq` commands:
```shell
    help                Print loq command help
    init                Generate your loq key
    encrypt             Encrypt a non-.loq file with the loq key
    decrypt             Decrypt a .loq file with the loq key
    print               Print decrypted contents of a .loq file
    view                View decrypted contents of a .loq file in page viewer
    edit                Edit encrypted .loq file in place. Uses $EDITOR
                        (default: vim)
    diff                Finds differences between two files. Either file can
                        be an encrypted loq file.
    find                recursively searches directory for .loq files and
                        searches each of those files for search_term
```

#### Examples
```shell
# Create loq key
loq init

# encrypt a file
loq encrypt myfile.yaml
> Creates myfile.yaml.loq

# decrypt a file
loq decrypt myfile.yaml.loq
> Creates myfile.yaml.open

# Diff encrypted file with open file
loq diff myfile.yaml.loq myfile.yaml.open

# Search through encrypted files for string
loq find search_term directory/to/search/
```
---

## loqet: secret store
`loqet` is an encrypted secret store tool. You can create a multiple secret stores that have their own associated secret keys.

`loqet context`

`loqet context` commands:
```shell
    help                Print out loqet context command help
    init                Initialize a loqet context
    get                 Get the active context name
    list                List the set of contexts
    info                Get detailed info about a context
    set                 Set the active context
    unset               Unset the active context
```

`loqet` commands:
```shell
    help                Print command usage
    list                List loqets in context
    ls                  List files in context directory
    create              Create a new loqet in a context
    encrypt             Encrypt an open loqet
    decrypt             Decrypt a locked loqet
    close               Encrypt all open loqets in a context
    open                Decrypt all locked loqets in a context
    print               Print contents of loqet to terminal
    view                View loqet contents in a page viewer
    edit                edit loqet namespace in editor (modifies .loq file only)
    get                 Get a value from a loqet config
    diff                Compare the open and closed configs for a single loqet
    find                Search a context for a matching string
    
Additional Args:
    --context CONTEXT_NAME    Execute the loqet command in a target context
                              rather than the active context
    --loq / --open            Target the .loq or .open file for a read-like command 
                              (works with print, view, and get)
```

#### Examples
```shell
# Create a loqet context named "myproject"
loqet context init myproject /path/to/myproject/secret_dir
> creates a context config in ~/.loqet/contexts.yaml
> creates a key at ~/.loqet/myproject.key

# Set new loqet context to active context
loqet context set myproject
> Now loqet commands will default to use the "myproject" context

# Create a loqet (a namespace with secrets inside) named "passwords"
loqet create passwords
> Creates a "passwords.yaml.open" file in the "myproject" context dir

# Add contents to passwords.yaml.open
cat <<EOF >>passwords.yaml.open
---
mysql:
  users:
    - username: rei
      password: eva00
    - username: shinji
      password: eva01
    - username: asuka
      password: eva02
EOF

# Encrypt the passwords loqet
loqet encrypt passwords
> Creates a "passwords.yaml.loq" file in the "myproject" context dir

# Decrypt the passwords loqet
loqet decrypt passwords
> Decrypts the contents of "passwords.yaml.loq" and writes it to "passwords.yaml.open"

# Print contents of passwords loqet to screen.
# Consider using `loqet view` instead, to view loqet contents in a page viewer
loqet print passwords

# Encrypt all .open files in a loqet context
loqet close

# Decrypt all .loq files in a loqet context
loqet open

# Get specific value from loqet
loqet get passwords.users.0.username
> prints "rei"

# Finds differences between the contents of the .open
# and .loq files for a specific loqet
loqet diff passwords

# Search the active loqet context for a search string
loqet find username
> prints:
>     - username: rei
>     - username: shinji
>     - username: asuka
```

#### Loqet Notes
When `loqet` commands that read or retrieve contents from a loqet (`print`, `view`, and `get`), the highest priority file will be read from:
1. loqet_name.yaml.open
2. loqet_name.yaml
3. loqet_name.yaml.loq 

This allows you to modify the unencrypted `.open` file to test changes, and then `loqet encrypt` that loqet to prepare your changes for version control.

If you want to view either the `loq` or `open` file specifically, rather than the one with highest precedence, you can pass the `--loq` or `--open` flags to force target that file.

For example:
```shell
loqet get passwords.users.0.username --loq
```
This will get the `users.0.username` config from the `passwords.yaml.loq` file in your active context, even if there is a `passwords.yaml.open` file in the context (the `open` file would normally have higher priority).

---

## Loq or Loqet, which should I use?
`loq` is great for encrypting single files that stand alone and don't need programmatic access. Lock up some passwords, bank account info, or crypto seed phrases to look at later when you need them. Alternatively, if you (securely) give a friend a loq key, you can send each other secret messages. I'll leave that up to you to figure out.

`loqet` is great for projects with secrets in their configs, or when you have groups of many secrets. It's also great for secret management in a project shared between multiple contributors, since you can securely share the keyfile, and commit encrypted secrets to a shared version control system.

---
## Configuration

Environment variables:
* `LOQET_CONFIG_DIR`: [default: `~/.loqet`] Location of directory containing loqet keys and configs
* `LOQ_KEY_FILE`: [default: `${LOQET_CONFIG_DIR}/loq.key`] Location of `loq` secret key
* `LOQET_CONFIG_FILE`: [default: `${LOQET_CONFIG_DIR}/contexts.yaml`] location of loqet context config file
* SAFE_MODE: [default: `False`] Enforces backing up keys and any files that would be overwritten during `loq` commands. Enforces updating `.gitignore` files on `loq` commands. 