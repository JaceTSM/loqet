"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""

import os
from cryptography.fernet import Fernet
from loqet.loqet_configs import LOQET_CONFIG_DIR, LOQ_KEY_FILE
from loqet.file_utils import backup_file


def generate_secret_key() -> bytes:
    """
    Generate Fernet secret key for encrypting and decrypting messages

    :return: [bytes] fernet secret key
    """
    return Fernet.generate_key()


def write_secret_key(context_name: str, secret_key: bytes = None) -> str:
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
    keyfile_path = os.path.join(LOQET_CONFIG_DIR, keyfile)

    # If there is a secret from an old context with the same name, back it up
    if os.path.exists(keyfile_path):
        backup_file(keyfile_path)

    with open(keyfile_path, "wb") as f:
        f.write(secret_key)

    return keyfile_path


def write_loq_key() -> bool:
    """
    Generate base secret key for encrypting and decrypting loq files
    that are not associated with a loqet context (writes to $LOQ_KEY_FILE)

    :return:    [bool] success
    """
    secret_key = generate_secret_key()
    if os.path.exists(LOQ_KEY_FILE):
        success = False
    else:
        if not os.path.exists(LOQET_CONFIG_DIR):
            os.mkdir(LOQET_CONFIG_DIR)
        with open(LOQ_KEY_FILE, "wb") as f:
            f.write(secret_key)
        success = True
    return success


def get_loq_key() -> bytes:
    """
    Retrieve base secret key for encrypting and decrypting loq files
    from loq config ($LOQ_KEY_FILE)

    :return: [bytes] loq secret key
    """
    if not os.path.exists(LOQ_KEY_FILE):
        write_loq_key()
    with open(LOQ_KEY_FILE, "rb") as f:
        secret_key = f.read()
    return secret_key
