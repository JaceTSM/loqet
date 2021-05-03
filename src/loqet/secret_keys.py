import os
from cryptography.fernet import Fernet
from loqet.loqet_configs import LOQET_CONFIG_DIR, LOQET_KEY_FILE
from loqet.utilities import backup_file


def generate_secret_key():
    return Fernet.generate_key()


def write_secret_key(context_name, secret_key=None):
    """
    Associates a secret key with a context.
    * Writes key to $LOQET_CONFIG_DIR/<context_name>.key
    * If there is a conflicting keyfile, it creates a backup

    :param context_name: name of context to write keyfile for
    :param secret_key:   encryption key to manage secrets in target context
    :return keyfile:     resulting keyfile name
    """
    if not os.path.exists(LOQET_CONFIG_DIR):
        os.mkdir(LOQET_CONFIG_DIR)

    if not secret_key:
        secret_key = generate_secret_key()

    keyfile = f"{context_name}.key"
    keyfile_path = os.path.join(LOQET_CONFIG_DIR, f"{context_name}.key")

    # If there is a secret from an old context with the same name, back it up
    if os.path.exists(keyfile_path):
        backup_file(keyfile_path)

    with open(keyfile_path, "wb") as f:
        f.write(secret_key)

    return keyfile


def write_master_key(secret_key=None):
    if not secret_key:
        secret_key = generate_secret_key()
    if os.path.exists(LOQET_KEY_FILE):
        backup_file(LOQET_KEY_FILE)
    with open(LOQET_KEY_FILE, "wb") as f:
        f.write(secret_key)


def get_master_key():
    if not os.path.exists(LOQET_KEY_FILE):
        write_master_key()
    with open(LOQET_KEY_FILE, "rb") as f:
        secret_key = f.read()
    return secret_key
