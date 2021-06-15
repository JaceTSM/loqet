# Loqet API

### loqet context methods
#### `create_loqet_context(context_name: str, loqet_dir: str) -> None`
Creates a loqet context named `context_name` with a secret store directory at `loqet_dir`.

#### `get_active_context_name() -> str`
Returns the name of the active context.

#### `get_context_info(context_name: str = None) -> dict`
Returns context metadata for target context.

sample output:
```python
{
    "loqet_dir": "/path/to/loqet/dir",
    "keyfile": "/path/to/loqet/keyfile",
}
```

#### `set_loqet_context(name: str) -> bool`
Set global loqet context to named context. Returns success boolean.

#### `unset_loqet_context() -> None`
Unsets global loqet context.

#### `get_loqet_contexts() -> dict`
Returns a dict of metadata of all contexts.

sample output:
```python
{
    "context_1": {
        "loqet_dir": "/path/to/loqet/dir",
        "keyfile": "/path/to/loqet/keyfile",
    },
    "context_2": {
        ...
    },
}
```

---

### loqet secret store methods
All methods with a `context_name` parameter default to using the active context.

#### `list_loqet_filenames(loqet_name: str, context_name: str = None) -> List[str]`
List all valid config files for a loqet in a loqet context.

#### `get_precedent_loqet_filename(loqet_name: str, context_name: str = None) -> str`
Returns loqet filename with the highest precedence.

#### `read_loqet(loqet_name: str, context_name: str = None, target: str = "default") -> str`
Read highest precedence loqet file as a string.

`target` options:
* `"default"` - targets highest precedence loqet file
* `"loq"` - target `.loq` file
* `"open"` - target `.open` file

#### `load_loqet(loqet_name: str, context_name: str = None, target: str = "default") -> dict`
Read highest precedence loqet file and load as a dictionary.

`target` options the same as `read_loqet`

#### `list_loqets(context_name: str = None) -> List[str]`
Returns list of loqet names in context

#### `list_loqet_dir(context_name: str = None, full_paths: bool = False) -> List[str]`
Returns all filenames in loqet dir

#### `create_loqet(loqet_name: str, context_name: str = None) -> bool`
Create a loqet namespace in a loqet context. Returns success boolean.

#### `encrypt_loqet(loqet_name: str, context_name: str = None, safe: bool = False) -> bool`
Encrypt open config file for a loqet namespace. Returns success boolean.

#### `decrypt_loqet(loqet_name: str, context_name: str = None, safe: bool = False) -> bool`
Decrypt encrypted config file for a loqet namespace. Returns success boolean.

#### `close_loqets(context_name: str = None, safe: bool = True) -> List[Tuple[str, bool]]`
Encrypts all .open files in named loqet context. Returns a list of tuples, pairing loqet names and success per loqet encrypted.

#### `open_loqets(context_name: str = None, safe: bool = True) -> List[Tuple[str, bool]]`
Decrypts all .loq files in named loqet context. Returns a list of tuples, pairing loqet names and success per loqet decrypted.

#### `loqet_get(loqet_namespace_path: str, context_name: str = None, target: str = "default") -> Union[str, dict]`
Get contents of loqet config at dot-delimited namespace path (eg. `loqet_name.path.to.config`). Invalid paths return empty dict. Lists can be accessed via numeric index (eg. `loqet_get("loqet_name.path.to.list.0.foo")`)


#### Examples
```python
import loqet

loqet.create_loqet_context("myproject")
loqet.set_loqet_context("myproject")
loqet.create_loqet("passwords")

passwords_open_file = [
    filename 
    for filename in loqet.list_loqet_filenames()
    if filename.endswith(".open")
][0]

with open(passwords_open_file, "w") as f:
    f.write("""---
mysql:
  users:
    - username: rei
      password: eva00
    - username: shinji
      password: eva01
    - username: asuka
      password: eva02
""")

loqet.encrypt_loqet("passwords")
sample_config = loqet.loqet_get("passwords.mysql.users.1.username")
print(sample_config)    # prints "shinji"
```
