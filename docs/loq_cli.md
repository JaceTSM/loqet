
## loq: encryption tool
`loq` is a command line encryption tool. It allows you to encrypt/decrypt files, view and edit encrypted files, diff encrypted files, and search through encrypted files. Files encrypted with the `loq` tool have the `.loq` extension. When you decrypt a `.loq` file, a `.open` file is created. This serves two functions:
1. If you encrypt, edit, then decrypt a file, you don't overwrite the original file contents.
2. If you are using git, You can add `*.open` to your `.gitignore`, preventing unencrypted secrets from being committed. (You will still need to manage the original, non-`.open` file, whether you delete it, gitignore it, or move it elsewhere is up to you)

To use the `loq` encryption tool, you must first set up a `loq key`, which will be used to encrypt and decrypt files when using the `loq` tool. You can generate a key with `loq init`. The key will be saved to `~/.loqet/loq.key` by default (env var `LOQ_KEY_FILE`).

## CLI
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
#> Creates myfile.yaml.loq

# decrypt a file
loq decrypt myfile.yaml.loq
#> Creates myfile.yaml.open

# Diff encrypted file with open file
loq diff myfile.yaml.loq myfile.yaml.open

# Search through encrypted files for string
loq find search_term directory/to/search/
```
