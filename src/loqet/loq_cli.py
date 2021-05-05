import argparse
import os
import sys

pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)

from loqet.loqet_configs import LOQET_KEY_FILE  # noqa
from loqet.encryption_suite import (
    loq_encrypt_file, loq_decrypt_file, loq_view_file, loq_print_file,
    loq_edit_file, loq_diff, loq_find
)   # noqa
from loqet.secret_keys import write_loq_key, get_loq_key  # noqa
from loqet.cli_utils import SAFE_ARG, subparser_setup   # noqa


loq_commands = {
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


def loq_parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Sub-command help", dest="command")
    subparser_setup(subparsers, loq_commands)
    args = parser.parse_args()
    return args


def loq_command_router(args):
    loq_key = get_loq_key()
    if args.command == "init":
        write_loq_key()
    elif args.command == "encrypt":
        loq_encrypt_file(args.encrypt_file_path, loq_key, safe=args.safe)
    elif args.command == "decrypt":
        loq_decrypt_file(args.decrypt_file_path, loq_key, safe=args.safe)
    elif args.command == "print":
        loq_print_file(args.print_file_path, loq_key)
    elif args.command == "view":
        loq_view_file(args.view_file_path, loq_key)
    elif args.command == "edit":
        # TODO: enable loq encrypt/decrypt on file globs
        loq_edit_file(args.edit_file_path, loq_key, safe=args.safe)
    elif args.command == "diff":
        loq_diff(args.diff_file_path_1, args.diff_file_path_2, loq_key)
    elif args.command == "find":
        loq_find(args.search_term, args.find_file_path, loq_key)


# Entry point for loq command in setup.py
def loq_cli():
    args = loq_parse_args()
    loq_command_router(args)


if __name__ == "__main__":
    loq_cli()
