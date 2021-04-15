import os
import tempfile
from subprocess import call
from cryptography.fernet import Fernet

from src.loqet.loqet_configs import SAFE_MODE, EDITOR
from src.loqet.exceptions import LoqetInvalidExtensionException
from src.loqet.utilities import read_file, write_file, backup_file, update_gitignore


####################
# Encryption Suite #
####################
"""
Fernet encryption is a symmetric encryption suite. This tool 
creates a fernet key and saves it to `~/.loqet/fernet.key`, 
and will use that keyfile to encrypt and decrypt configs.
"""


def encrypt_message(message, secret_key):
    f = Fernet(secret_key)
    return f.encrypt(message.encode())


def decrypt_message(encrypted_message, secret_key):
    if isinstance(encrypted_message, str):
        encrypted_message = encrypted_message.encode()
    f = Fernet(secret_key)
    return f.decrypt(encrypted_message).decode()


def read_loq_file(locked_file, secret_key):
    """Reads a .loq file and returns it's unencrypted contents"""
    return decrypt_message(read_file(locked_file), secret_key)


def write_loq_file(contents, filename, secret_key):
    """Encrypts content and writes it to a .loq file"""
    write_file(encrypt_message(contents, secret_key), filename)


# loq <filename>
def loq_file(filename, secret_key, safe=False):
    """
    Encrypts a file as a .vault next to it

    config.yaml         => config.yaml.loq
    config.yaml.open    => config.yaml.loq
    """
    if filename.endswith(".loq"):
        raise LoqetInvalidExtensionException(
            "{} already has the .loq extension. It is likely already encrypted."
        )
    if filename.endswith(".open"):
        locked_file = "{}.loq".format(filename[:-5])
    else:
        locked_file = "{}.loq".format(filename)
    contents = read_file(filename)
    if (safe or SAFE_MODE) and os.path.exists(locked_file):
        update_gitignore(filename)
        backup_file(locked_file)
    write_loq_file(contents, locked_file, secret_key)


# unloq <filename>
def unloq_file(locked_file, secret_key, safe=False):
    """
    Unencrypts a .loq file as a .open file next to it

    config.yaml.loq => config.yaml.open

    This allows you to add `.open` to your gitignore to safely
    unencrypt stuff with lower risk of committing secrets.
    """
    if not locked_file.endswith(".loq"):
        raise LoqetInvalidExtensionException(
            "Failed to decrypt: '{}'\nloqet files must have .loq extension"
            .format(locked_file)
        )
    decrypted_contents = read_loq_file(locked_file, secret_key)
    open_file = "{}.open".format(locked_file[:-4])
    if safe or SAFE_MODE:
        update_gitignore(locked_file)
        if os.path.exists(open_file):
            backup_file(open_file)
    write_file(decrypted_contents, open_file)


# loq edit <filename>
def edit_loq_file(locked_file, secret_key, safe=False):
    unencrypted_contents = read_loq_file(locked_file, secret_key)
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(unencrypted_contents)

        # Opens interactive editor for CLI user to edit file live
        call([EDITOR, tf.name])
        tf.seek(0)
        edited_message = tf.read()
    if safe or SAFE_MODE:
        update_gitignore(locked_file)
        backup_file(locked_file)
    write_loq_file(edited_message, locked_file, secret_key)
