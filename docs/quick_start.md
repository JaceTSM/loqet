## Quick Start Guide
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
