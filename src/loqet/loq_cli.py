"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

-------------------------------------------------

loq cli

Command line interface for the loq encryption suite.


# CLI Commands:
loq help        print command help text
loq init        generate or set loq key
loq encrypt     encrypt a file
loq decrypt     unencrypt a file
loq print       print encrypted file contents
loq view        view encrypted file contents in viewer
loq edit        edit encrypted file in place
loq diff        compare a loq and open file
loq find        searches for loq files that contain some text

"""

import argparse
import difflib
import pydoc
import sys
import tempfile
from subprocess import call

from loqet.file_utils import backup_file, update_gitignore, read_file
from loqet.loqet_configs import LOQ_KEY_FILE, EDITOR, SAFE_MODE
from loqet.encryption_suite import (
    loq_encrypt_file, loq_decrypt_file, read_loq_file,
    loq_file_search, write_loq_file, validate_loq_file
)
from loqet.secret_keys import write_loq_key, get_loq_key
from loqet.cli_utils import SAFE_ARG, subparser_setup


loq_commands = {
    "help": {
        "help": "Print loq command help",
        "subparser_args": [],
    },
    "init": {
        "help": "Generate your loq key",
        "subparser_args": [],
    },
    "encrypt": {
        "help": "Encrypt a non-.loq file with the loq key",
        "subparser_args": [
            "encrypt_file_path",
            SAFE_ARG,
        ],
    },
    "decrypt": {
        "help": "Decrypt a .loq file with the loq key",
        "subparser_args": [
            "decrypt_file_path",
            SAFE_ARG,
        ],
    },
    "print": {
        "help": "Print decrypted contents of a .loq file",
        "subparser_args": ["print_file_path"],
    },
    "view": {
        "help": "View decrypted contents of a .loq file in page viewer",
        "subparser_args": ["view_file_path"],
    },
    "edit": {
        "help": "Edit encrypted .loq file in place. Uses $EDITOR (default: vim)",
        "subparser_args": [
            "edit_file_path",
            SAFE_ARG,
        ],
    },
    "diff": {
        "help": "Finds differences between two files. "
                "Either file can be an encrypted loq file.",
        "subparser_args": [
            "diff_file_path_1",
            "diff_file_path_2"
        ],
    },
    "find": {
        "help": "recursively searches directory for .loq files "
                "and searches each of those files for search_term",
        "subparser_args": [
            "search_term",
            "find_file_path"
        ],
    },
}


###########
# Loq CLI #
###########

def loq_init_cli() -> None:
    """
    Initialize loq CLI tool by creating a base loq key.
    Takes no action if a loq key already exists at $LOQ_KEY_FILE

    :return:    n/a
    """
    success = write_loq_key()
    if success:
        print(f"Loq key written to {LOQ_KEY_FILE}. DO NOT LOSE THIS FILE. "
              f"If you encrypt something with this key, and you lose the key, "
              f"it is gone forever.")
    else:
        print(f"Key already exists at {LOQ_KEY_FILE}. "
              f"Please remove to re-initialize.")


def loq_encrypt_cli(file_path: str, safe: bool) -> None:
    """CLI for loq_encrypt_file"""
    loq_key = get_loq_key()
    loq_file = loq_encrypt_file(file_path, loq_key, safe)
    print(f"Wrote encrypted file {loq_file}")


def loq_decrypt_cli(loq_file_path: str, safe: bool) -> None:
    """CLI for loq_decrypt_file"""
    loq_key = get_loq_key()
    open_file = loq_decrypt_file(loq_file_path, loq_key, safe)
    print(f"Wrote open file to {open_file}")


def loq_print_cli(loq_file_path: str) -> None:
    """
    Print decrypted contents of loq file to console

    :param loq_file_path:   loq file to decrypt and print
    :return:                n/a
    """
    loq_key = get_loq_key()
    unencrypted_contents = read_loq_file(loq_file_path, loq_key)
    if unencrypted_contents is None:
        print(f"{loq_file_path} is not a valid loq file.")
    print(unencrypted_contents)


def loq_view_cli(loq_file_path: str) -> None:
    """
    View decrypted loq file contents in page viewer

    :param loq_file_path:   loq file to view
    :return:                n/a
    """
    loq_key = get_loq_key()
    unencrypted_contents = read_loq_file(loq_file_path, loq_key)
    if unencrypted_contents is None:
        print(f"{loq_file_path} is not a valid loq file.")
    pydoc.pager(unencrypted_contents)


def loq_edit_file(loq_file_path: str, secret_key: bytes, safe: bool) -> None:
    """
    Edit a loq file in place with an editor (set by env var $EDITOR)

    :param loq_file_path:   loq file to edit
    :param secret_key:      fernet key to decrypt/encrypt file
    :param safe:            If True, backup file overwrites and update gitignore
    :return:                n/a
    """
    unencrypted_contents = read_loq_file(loq_file_path, secret_key) or ""
    if unencrypted_contents is None:
        print(f"{loq_file_path} is not a valid loq file.")
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
            update_gitignore(loq_file_path)
            backup_file(loq_file_path)
        write_loq_file(edited_message, loq_file_path, secret_key)
        print(f"Wrote edits to {loq_file_path}")
    else:
        print("No changes, no action taken")


def loq_edit_cli(loq_file_path: str, safe: bool) -> None:
    """
    CLI for loq_edit_file
    """
    loq_key = get_loq_key()
    loq_edit_file(loq_file_path, loq_key, safe=safe)


def loq_diff(path_1: str, path_2: str, secret_key: bytes) -> str:
    """
    Print a unified diff of two files. Either file can be a loq file,
    in which case the decrypted contents are diffed.

    :param path_1:      path to first file
    :param path_2:      path to second file
    :param secret_key:  fernet key to decrypt/encrypt file
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
    return "".join(diff)


def loq_diff_cli(path_1: str, path_2: str) -> None:
    """CLI for loq_diff"""
    loq_key = get_loq_key()
    pydoc.pager(loq_diff(path_1, path_2, loq_key))


def loq_find_cli(search_term: str, target_dir: str) -> None:
    """
    Search for search_term in all encrypted loq files in target_dir (recursively)

    :param search_term:     string to search for in loq files
    :param target_dir:      dirctory to search (recursively)
    :return:                n/a (prints results)
    """
    loq_key = get_loq_key()
    matches = []
    match_lines = {}
    loq_files = loq_file_search(target_dir)

    for loq_file in loq_files:
        loq_contents = read_loq_file(loq_file, loq_key)
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


#########################
# Command Parser/Router #
#########################

def loq_parse_args() -> argparse.Namespace:
    """Generate argparser namespace for `loq` command args"""
    parser = argparse.ArgumentParser(
        description="loq command",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(help="Sub-command help", dest="command")
    subparser_setup(subparsers, loq_commands)
    args = parser.parse_args()

    if args.command in ["help", None]:
        parser.print_help()
        sys.exit()

    return args


def loq_command_router(args: argparse.Namespace) -> None:
    """Route `loq` cli inputs to library calls"""
    if args.command == "init":
        loq_init_cli()
    elif args.command == "encrypt":
        loq_encrypt_cli(args.encrypt_file_path, safe=args.safe)
    elif args.command == "decrypt":
        loq_decrypt_cli(args.decrypt_file_path, safe=args.safe)
    elif args.command == "print":
        loq_print_cli(args.print_file_path)
    elif args.command == "view":
        loq_view_cli(args.view_file_path)
    elif args.command == "edit":
        loq_edit_cli(args.edit_file_path, safe=args.safe)
    elif args.command == "diff":
        loq_diff_cli(args.diff_file_path_1, args.diff_file_path_2)
    elif args.command == "find":
        loq_find_cli(args.search_term, args.find_file_path)


# Entry point for loq command in setup.py
def loq_cli() -> None:
    """Execute `loq` command line interface."""
    args = loq_parse_args()
    loq_command_router(args)


if __name__ == "__main__":
    loq_cli()
