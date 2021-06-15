# loqet: secret store
`loqet` is an encrypted secret store tool. You can create a multiple secret stores that have their own associated secret keys.

A `loqet context` is a collection of secret namespaces that are all managed together and encrypted with a single secret key. Simply put, a `loqet context` is a secret store that you can associate with a project.

---

### Loqet Notes
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

## CLI
`loqet context` CLI commands:
```shell
    help                Print out loqet context command help
    init                Initialize a loqet context
    get                 Get the active context name
    list                List the set of contexts
    info                Get detailed info about a context
    set                 Set the active context
    unset               Unset the active context
```

`loqet` CLI commands:
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
