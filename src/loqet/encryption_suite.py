"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

------------------------------------------------------

Encryption Suite: loq api

Tools for encrypting files, and interacting with encrypted
files not associated with a loqet context.

Base Encryption Suite API:
encrypt_message     encrypt string contents
decrypt_message     decrypt string contents
validate_loq_file   Determine if a file is valid to be decrypted
read_loq_file       get unencrypted contents of loq file
write_loq_file      encrypt contents and write them to a loq file
loq_encrypt_file    encrypt a file
loq_decrypt_file    decrypt a loq file
loq_file_search     find all valid loq files in a directory (recursive)

"""

import os
import yaml
from cryptography.fernet import Fernet
from typing import List

from loqet.loqet_configs import SAFE_MODE
from loqet.exceptions import LoqInvalidFileException
from loqet.file_utils import read_file, write_file, backup_file, update_gitignore


####################
# Encryption Suite #
####################
"""
Fernet encryption is a symmetric encryption suite. This tool 
creates a fernet key and saves it to `~/.loqet/loqet.key`, 
and will use that keyfile to encrypt and decrypt configs.
"""

LOQ_HEADER = "#loq;"


def encrypt_message(message: str, secret_key: bytes) -> str:
    """
    Encrypt a message with Fernet symmetric encryption.

    :param message:     String to encrypt
    :param secret_key:  A valid Fernet encryption key
    :return:            Encrypted string
    """
    f = Fernet(secret_key)
    return f.encrypt(message.encode()).decode()


def decrypt_message(encrypted_message: str, secret_key: bytes) -> str:
    """
    Decrypt an encrypted message with the key used to encrypt it.

    :param encrypted_message:   Encrypted string
    :param secret_key:          Key used to encrypt encrypted_message
    :return:                    Decrypted string
    """
    if isinstance(encrypted_message, str):
        encrypted_message = encrypted_message.encode()
    f = Fernet(secret_key)
    return f.decrypt(encrypted_message).decode()


def validate_loq_file(loq_file: str) -> bool:
    """
    Determine if a file is a valid loq file

    :param loq_file:    Path to file
    :return:            Bool
    """
    with open(loq_file, "r") as f:
        top_line = f.readline()
    return top_line.strip() == LOQ_HEADER


def read_loq_file(loq_file: str, secret_key: bytes) -> str:
    """
    Reads a .loq file and returns it's unencrypted contents

    :param loq_file:    Path to loq file
    :param secret_key:  key used to encrypt loq_file
    :return:            decrypted file contents
    """
    raw_file_contents = read_file(loq_file)
    if validate_loq_file(loq_file):
        encrypted_string = raw_file_contents.replace("\n", "").lstrip(LOQ_HEADER)
        decrypted_contents = decrypt_message(encrypted_string, secret_key)
    else:
        decrypted_contents = None
    return decrypted_contents


def write_loq_file(contents: str, filename: str, secret_key: bytes) -> None:
    """
    Encrypts content and writes it to a .loq file

    :param contents:    String to encrypt and write to file
    :param filename:    file to write to
    :param secret_key:  key to encrypt message with
    :return:            n/a
    """
    encrypted_message = encrypt_message(contents, secret_key)
    file_formatted_string = "\n".join(
        [LOQ_HEADER] +
        [
            str(encrypted_message[i:i + 64])
            for i in range(0, len(encrypted_message), 64)
        ]
    )
    write_file(file_formatted_string, filename)


# TODO: enable loq encrypt/decrypt on file globs
def loq_encrypt_file(filename: str, secret_key: bytes, safe: bool = False) -> str:
    """
    Encrypts a file as a .vault next to it

    config.yaml         => config.yaml.loq
    config.yaml.open    => config.yaml.loq

    :param filename:    File to encrypt
    :param secret_key:  Key to encrypt file contents with
    :param safe:        If True, backup on file overwrites and update .gitignore
    :return:            resulting loq file path
    """
    if filename.endswith(".open"):
        loq_file = "{}.loq".format(filename[:-5])
    else:
        loq_file = "{}.loq".format(filename)
    contents = read_file(filename)
    if (safe or SAFE_MODE) and os.path.exists(loq_file):
        update_gitignore(filename)
        backup_file(loq_file)
    write_loq_file(contents, loq_file, secret_key)
    return loq_file


def loq_decrypt_file(loq_file: str, secret_key: bytes, safe: bool = False) -> str:
    """
    Unencrypts a .loq file as a .open file next to it

    config.yaml.loq => config.yaml.open

    This allows you to add `.open` to your gitignore to safely
    unencrypt stuff with lower risk of committing secrets.

    :param loq_file:    loq file to decrypt
    :param secret_key:  key to decrypt loq file contents with
    :param safe:        If True, backup file overwrites and update gitignore
    :return:            resulting open file path
    """
    if not validate_loq_file(loq_file):
        raise LoqInvalidFileException(
            "Failed to decrypt: '{}'\nloqet files must have .loq extension"
            .format(loq_file)
        )
    decrypted_contents = read_loq_file(loq_file, secret_key)
    open_file = "{}.open".format(loq_file[:-4])
    if safe or SAFE_MODE:
        update_gitignore(loq_file)
        if os.path.exists(open_file):
            backup_file(open_file)
    # If we go to overwrite an existing file with empty contents,
    # we make a backup anyway, just in case.
    if not decrypted_contents and os.path.exists(open_file):
        backup_file(open_file)
    write_file(decrypted_contents, open_file)
    return open_file


def load_loq_config(loq_path: str, secret_key: bytes) -> dict:
    """
    Decrypts a vaulted config file and loads it as dict.

    :param loq_path:        name of loqet to load
    :param secret_key:      secret key to decrypt loq file
    :return:                [dict] unencrypted loqet contents
    """
    loq_contents = read_loq_file(loq_path, secret_key)
    config = yaml.safe_load(loq_contents)
    return config


def loq_file_search(target_dir: str) -> List[str]:
    """
    Recursively search for all valid loq files at target dir

    :param target_dir:  Directory to search for loq files
    :return:            List of loq file paths
    """
    loq_files = []
    for root, dirs, files in os.walk(target_dir):
        for name in files:
            file_path = os.path.join(root, name)
            if ".loq" in file_path and validate_loq_file(file_path):
                loq_files.append(file_path)
    return loq_files
