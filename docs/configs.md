---
# Loqet Configuration

Environment variables:
* `LOQET_CONFIG_DIR`: [default: `~/.loqet`] Location of directory containing loqet keys and configs
* `LOQ_KEY_FILE`: [default: `${LOQET_CONFIG_DIR}/loq.key`] Location of `loq` secret key
* `LOQET_CONFIG_FILE`: [default: `${LOQET_CONFIG_DIR}/contexts.yaml`] location of loqet context config file
* SAFE_MODE: [default: `False`] Enforces backing up keys and any files that would be overwritten during `loq` commands. Enforces updating `.gitignore` files on `loq` commands. 
