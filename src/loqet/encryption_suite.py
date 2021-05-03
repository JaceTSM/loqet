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
loq encrypt         encrypt a file
loq decrypt         unencrypt a file
loq print           print encrypted file contents
loq view            view encrypted file contents in viewer
loq edit            edit encrypted file in place
loq diff            compare a loq and open file
loq find            searches for loq files that contain some text

TODO:
  Determine how to do find operations. Decrypting every file to search is
  crazy slow, so it might make sense to make an index, which would then need
  to be encrypted. Managing that index is another huge set of challenges
"""

import difflib
import os
import pydoc
import sys
import tempfile
from subprocess import call
from cryptography.fernet import Fernet

from loqet.loqet_configs import SAFE_MODE, EDITOR
from loqet.exceptions import LoqetInvalidExtensionException
from loqet.utilities import read_file, write_file, backup_file, update_gitignore


####################
# Encryption Suite #
####################
"""
Fernet encryption is a symmetric encryption suite. This tool 
creates a fernet key and saves it to `~/.loqet/loqet.key`, 
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


###########
# loq cli #
###########

# loq encrypt <filename>
def loq_encrypt_file(filename, secret_key, safe=False):
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


# loq decrypt <filename>
def loq_decrypt_file(locked_file, secret_key, safe=False):
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
def loq_edit_file(locked_file, secret_key, safe=False):
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


# loq print <filename>
def loq_print_file(locked_file, secret_key):
    unencrypted_contents = read_loq_file(locked_file, secret_key)
    print(unencrypted_contents)


# loq view <filename>
def loq_view_file(locked_file, secret_key):
    unencrypted_contents = read_loq_file(locked_file, secret_key)
    pydoc.pager(unencrypted_contents)


# loq diff <filepath_1(.loq)> <filepath_2(.loq)>
def loq_diff(path_1, path_2, secret_key):
    if path_1.endswith(".loq"):
        contents_1 = read_loq_file(path_1, secret_key)
    else:
        contents_1 = read_file(path_1)

    if path_2.endswith(".loq"):
        contents_2 = read_loq_file(path_2, secret_key)
    else:
        contents_2 = read_file(path_2)
    diff = difflib.unified_diff(
        contents_1,
        contents_2,
        fromfile=path_1,
        tofile=path_2
    )
    sys.stdout.writelines(diff)


# loq find <search_term> <path>
def loq_find(seach_term, target_dir, secret_key):
    loq_files = []
    matches = []
    match_lines = {}
    for root, dirs, files in os.walk(target_dir):
        for name in files:
            file_path = os.path.join(root, name)
            if file_path.endswith(".loq"):
                loq_files.append(file_path)

    for loq_file in loq_files:
        loq_contents = read_loq_file(loq_file, secret_key)
        for line_num, line in loq_contents.split("\n"):
            if seach_term in line:
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
            print(f"\t{str(line_num).ljust(4)}: {line}")
