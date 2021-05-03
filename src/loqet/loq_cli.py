import argparse
import os
import sys

pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)

from loqet.encryption_suite import (
    loq_encrypt_file, loq_decrypt_file, loq_view_file, loq_print_file,
    loq_edit_file, loq_diff, loq_find
)
from loqet.secret_keys import get_master_key


def loq_parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--safe", action="store_true")
    subparsers = parser.add_subparsers(help="Sub-command help")

    # TODO: enable loq encrypt/decrypt on file globs
    # loq encrypt filename(.open)
    encrypt_subparser = subparsers.add_parser(
        "encrypt",
        help="Encrypt a non-.loq file with the loqet master key"
    )
    encrypt_subparser.add_argument("encrypt_file_path")

    # loq decrypt filename.loq
    decrypt_subparser = subparsers.add_parser(
        "decrypt",
        help="Decrypt a .loq file with the loqet master key"
    )
    decrypt_subparser.add_argument("decrypt_file_path")

    # loq print filename.loq
    print_subparser = subparsers.add_parser(
        "print",
        help="Print decrypted contents of a .loq file"
    )
    print_subparser.add_argument("print_file_path")

    # loq view filename.loq
    view_subparser = subparsers.add_parser(
        "view",
        help="View decrypted contents of a .loq file in page viewer"
    )
    view_subparser.add_argument("view_file_path")

    # loq edit filename.loq
    edit_subparser = subparsers.add_parser(
        "edit",
        help="Edit encrypted .loq file in place. Uses $EDITOR (default: vim)"
    )
    edit_subparser.add_argument("edit_file_path")

    # loq diff filename(.loq)
    diff_subparser = subparsers.add_parser(
        "diff",
        help="Finds differences between two files. Either file can "
             "be an encrypted loq file."
    )
    diff_subparser.add_argument("diff_file_path_1")
    diff_subparser.add_argument("diff_file_path_2")

    # loq find search_term path
    find_subparser = subparsers.add_parser(
        "find",
        help="recursively searches directory for .loq files "
             "and searches each of those files for search_term"
    )
    find_subparser.add_argument("search_term")
    find_subparser.add_argument("find_file_path")

    args = parser.parse_args()
    return args


def loq_command_router(args):
    master_key = get_master_key()
    if hasattr(args, "encrypt_file_path"):
        loq_encrypt_file(args.encrypt_file_path, master_key, safe=args.safe)
    elif hasattr(args, "decrypt_file_path"):
        loq_decrypt_file(args.decrypt_file_path, master_key, safe=args.safe)
    elif hasattr(args, "print_file_path"):
        loq_print_file(args.edit_file_path, master_key)
    elif hasattr(args, "view_file_path"):
        loq_view_file(args.view_file_path, master_key)
    elif hasattr(args, "edit_file_path"):
        loq_edit_file(args.edit_file_path, master_key, safe=args.safe)
    elif hasattr(args, "diff_file_path_1"):
        loq_diff(args.diff_file_path_1, args.diff_file_path_2, master_key)
    elif hasattr(args, "find_file_path"):
        loq_find(args.search_term, args.find_file_path, master_key)


# Entry point for loq command in setup.py
def loq_cli():
    args = loq_parse_args()
    loq_command_router(args)


if __name__ == "__main__":
    loq_cli()
