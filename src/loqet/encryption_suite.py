"""
Encryption Suite (loq api)

Tools for encrypting files, and interacting with encrypted
files not associated with a loqet context.

Base Encryption Suite API:
encrypt_message     encrypt string contents
decrypt_message     decrypt string contents
read_loq_file       get unencrypted contents of loq file
write_loq_file      encrypt contents and write them to a loq file

CLI:
loq init            generate or set loq key
loq encrypt         encrypt a file
loq decrypt         unencrypt a file
loq print           print encrypted file contents
loq view            view encrypted file contents in viewer
loq edit            edit encrypted file in place
loq diff            compare a loq and open file
loq find            searches for loq files that contain some text
"""

import difflib
import os
import pydoc
import sys
import tempfile
from subprocess import call
from cryptography.fernet import Fernet
from typing import List

from loqet.loqet_configs import SAFE_MODE, EDITOR
from loqet.exceptions import LoqetInvalidExtensionException
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
        print(f"{loq_file} is not a valid loq file")
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


###########
# loq cli #
###########

# loq encrypt <filename>
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
    print(f"Wrote encrypted file {loq_file}")
    return loq_file


# loq decrypt <filename>
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
    if not loq_file.endswith(".loq"):
        raise LoqetInvalidExtensionException(
            "Failed to decrypt: '{}'\nloqet files must have .loq extension"
            .format(loq_file)
        )
    decrypted_contents = read_loq_file(loq_file, secret_key)
    open_file = "{}.open".format(loq_file[:-4])
    if safe or SAFE_MODE:
        update_gitignore(loq_file)
        if os.path.exists(open_file):
            backup_file(open_file)
    write_file(decrypted_contents, open_file)
    print(f"Wrote unencrypted file to {open_file}")
    return open_file


# loq edit <filename>
def loq_edit_file(loq_file: str, secret_key: bytes, safe: bool = False) -> None:
    """
    Edit a loq file in place with an editor (set by env var $EDITOR)

    :param loq_file:    loq file to edit
    :param secret_key:  key used to encrypt/decrypt loq file contents
    :param safe:        If True, backup file overwrites and update gitignore
    :return:            n/a
    """
    unencrypted_contents = read_loq_file(loq_file, secret_key)
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.seek(0)
        tf.write(unencrypted_contents.encode())
        tf.flush()
        # Opens interactive editor for CLI user to edit file live
        call([EDITOR, tf.name])
        tf.seek(0)
        edited_message = tf.read().decode()
    if edited_message != unencrypted_contents:
        if safe or SAFE_MODE:
            update_gitignore(loq_file)
            backup_file(loq_file)
        write_loq_file(edited_message, loq_file, secret_key)
        print(f"Wrote edits to {loq_file}")
    else:
        print("No changes, no action taken")


# loq print <filename>
def loq_print_file(loq_file: str, secret_key: bytes) -> None:
    """
    Print decrypted contents of loq file to console

    :param loq_file:    loq file to decrypt and print
    :param secret_key:  key used to decrypt loq_file contents
    :return:            n/a
    """
    unencrypted_contents = read_loq_file(loq_file, secret_key)
    print(unencrypted_contents)


# loq view <filename>
def loq_view_file(loq_file: str, secret_key: bytes) -> None:
    """
    View decrypted loq file contents in page viewer

    :param loq_file:    loq file to view
    :param secret_key:  key used to decrypt loq_file contents
    :return:            n/a
    """
    unencrypted_contents = read_loq_file(loq_file, secret_key)
    pydoc.pager(unencrypted_contents)


# loq diff <filepath_1(.loq)> <filepath_2(.loq)>
def loq_diff(path_1: str, path_2: str, secret_key: bytes) -> None:
    """
    Print a unified diff of two files. Either file can be a loq file,
    in which case the decrypted contents are diffed.

    :param path_1:      path to first file
    :param path_2:      path to second file
    :param secret_key:  secret key used to decrypt those two files
    :return:            n/a
    """
    if validate_loq_file(path_1):
        contents_1 = read_loq_file(path_1, secret_key)
    else:
        contents_1 = read_file(path_1)

    if validate_loq_file(path_2):
        contents_2 = read_loq_file(path_2, secret_key)
    else:
        contents_2 = read_file(path_2)
    contents_1 = [line + "\n" for line in contents_1.split("\n")]
    contents_2 = [line + "\n" for line in contents_2.split("\n")]
    diff = difflib.unified_diff(
        contents_1,
        contents_2,
        fromfile=path_1,
        tofile=path_2
    )
    sys.stdout.writelines(diff)


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


# loq find <search_term> <path>
def loq_find(search_term: str, target_dir: str, secret_key: bytes) -> None:
    """

    :param search_term:
    :param target_dir:
    :param secret_key:
    :return:
    """
    matches = []
    match_lines = {}
    loq_files = loq_file_search(target_dir)

    for loq_file in loq_files:
        loq_contents = read_loq_file(loq_file, secret_key)
        for line_num, line in enumerate(loq_contents.split("\n")):
            if search_term in line:
                if loq_file not in matches:
                    matches.append(loq_file)
                if loq_file not in match_lines:
                    match_lines[loq_file] = {line_num: line}
                else:
                    match_lines[loq_file][line_num] = line

    print(f"Found {len(matches)} matching .loq files.")
    for match in matches:
        print(f"{match}:")
        for line_num, line in match_lines[match].items():
            print(f"{' '*4}{str(line_num).rjust(4)}: {line}")
