"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

---------------------------------------------------

loqet cli

Command line tools for interacting with loqet secret stores


# CLI Commands:
loqet help      print help text
loqet list      list loqet namespaces
loqet ls        list files in loqet dir
loqet create    create a loqet namespace
loqet encrypt   encrypt a single loqet namespace
loqet decrypt   decrypt a single loqet namespace
loqet close     encrypt all open files in loqet dir
loqet open      decrypt all loq files in loqet dir
loqet print     print contents of loqet namespace
loqet view      read contents of target loqet namespace in viewer (.loq file)
loqet edit      edit loqet namespace in editor (modifies .loq file only)
loqet get       print value from a loqet namespace (pass dot delimited path)
loqet set     **Not supported
loqet diff      determine where loq and open files differ
loqet find      search loqets for text (keys and values)


Notes:
** We don't support direct setting loqet config values via CLI or API because
   it would be an opaque process, and if used in automation could lead to
   scenarios where secrets are unintentionally overwritten and lost.
   If you want to change a secret in an encrypted loqet, use `loqet edit`
   or `loqet decrypt` and `loqet encrypt`.

"""

import argparse
import json
import os
import pydoc
import sys
import yaml

from loqet.cli_utils import (
    SAFE_ARG, UNSAFE_ARG, LOQ_ARG, OPEN_ARG, subparser_setup
)
from loqet.encryption_suite import read_loq_file
from loqet.exceptions import LoqetInvalidArgumentException, LoqetNoSetContextException
from loqet.file_utils import read_file
from loqet.loqet_contexts import get_context
from loqet.loqet_context_cli import context_command_parser, context_command_router
from loqet.secret_store import (
    list_loqets, list_loqet_dir, create_loqet, encrypt_loqet, decrypt_loqet,
    close_loqets, open_loqets, loqet_get, list_loqet_filenames, read_loqet
)
from loqet.loq_cli import loq_edit_file, loq_diff


# TODO: Move these to yaml files and convert SAFE/UNSAFE_ARGs into
#       special cases with just --safe/--unsafe (boo special cases)
loqet_commands = {
    "help": {
        "help": "Print command usage",
        "subparser_args": [],
    },
    "list": {
        "help": "List loqets in context",
        "subparser_args": ["--context"],
    },
    "ls": {
        "help": "List files in context directory",
        "subparser_args": [
            "--context",
            {
                "args": ["-p", "--paths"],
                "kwargs": {
                    "action": "store_true",
                    "help": "Print full paths instead of just filenames"
                },
            },
        ],
    },
    "create": {
        "help": "Create a new loqet in a context",
        "subparser_args": [
            "create_loqet_name",
            "--context",
        ],
    },
    "encrypt": {
        "help": "Encrypt an open loqet",
        "subparser_args": [
            "encrypt_loqet_name",
            "--context",
            SAFE_ARG,
        ],
    },
    "decrypt": {
        "help": "Decrypt a locked loqet",
        "subparser_args": [
            "decrypt_loqet_name",
            "--context",
            SAFE_ARG,
        ],
    },
    "close": {
        "help": "Encrypt all open loqets in a context",
        "subparser_args": [
            "--context",
            UNSAFE_ARG,
        ],
    },
    "open": {
        "help": "Decrypt all locked loqets in a context",
        "subparser_args": [
            "--context",
            UNSAFE_ARG,
        ],
    },
    "print": {
        "help": "Print contents of loqet to terminal",
        "subparser_args": [
            "print_loqet_name",
            "--context",
            {
                "args": ["-j", "--json"],
                "kwargs": {
                    "action": "store_true",
                    "help": "Print contents as json"
                },
            },
            LOQ_ARG,
            OPEN_ARG,
        ],
    },
    "view": {
        "help": "View loqet contents in a page viewer",
        "subparser_args": [
            "view_loqet_name",
            "--context",
            LOQ_ARG,
            OPEN_ARG,
        ],
    },
    "edit": {
        "help": "edit loqet namespace in editor (modifies .loq file only)",
        "subparser_args": [
            "edit_loqet_name",
            "--context",
            SAFE_ARG,
        ],
    },
    "get": {
        "help": "Get a value from a loqet config",
        "subparser_args": [
            "get_namespace_path",
            "--context",
            LOQ_ARG,
            OPEN_ARG,
        ],
    },
    # # NOT YET SUPPORTED
    # "set": {
    #     "help": "",
    #     "subparser_args": [],
    # },
    "diff": {
        "help": "Compare the open and closed configs for a single loqet",
        "subparser_args": [
            "diff_loqet_name",
            "--context",
        ],
    },
    "find": {
        "help": "Search a context for a matching string",
        "subparser_args": [
            "find_search_term",
            "--context",
        ],
    },
}


#############
# Loqet CLI #
#############

def loqet_list_cli(context_name: str) -> None:
    """CLI for list_loqets"""
    context_loqets = list_loqets(context_name)
    print("\n".join(context_loqets))


def loqet_ls_cli(context_name: str, paths: bool = False) -> None:
    """CLI for list_loqet_dir"""
    context_dir_files = list_loqet_dir(context_name, full_paths=paths)
    print("\n".join(context_dir_files))


def loqet_create_cli(loqet_name: str, context_name: str) -> None:
    """CLI for create_loqet"""
    open_path = create_loqet(loqet_name, context_name)
    if open_path:
        print(f"Created '{loqet_name}' loqet at '{open_path}'")
    else:
        print(f"Failed to create '{loqet_name}' loqet. "
              f"Check to see if the loqet already exists with 'loqet list'.")


def loqet_encrypt_cli(loqet_name: str, context_name: str, safe: bool) -> None:
    """CLI for encrypt_loqet"""
    loq_path = encrypt_loqet(loqet_name, context_name, safe=safe)
    if loq_path:
        print(f"Encrypted '{loqet_name}' loqet to '{loq_path}'")
    else:
        print(f"Failed to encrypt '{loqet_name}' loqet")


def loqet_decrypt_cli(loqet_name: str, context_name: str, safe: bool) -> None:
    """CLI for decrypt_loqet"""
    open_path = decrypt_loqet(loqet_name, context_name, safe=safe)
    if open_path:
        print(f"Decrypted '{loqet_name}' loqet to '{open_path}'")
    else:
        print(f"Failed to decrypt '{loqet_name}' loqet")


def loqet_close_cli(context_name: str, unsafe: bool) -> None:
    """CLI for close_loqets"""
    print(f"Encrypting all loqets in '{context_name}' context")
    close_loqets(context_name, safe=not unsafe)


def loqet_open_cli(context_name: str, unsafe: bool) -> None:
    """CLI for open_loqets"""
    print(f"Decrypting all loqets in '{context_name}' context")
    open_loqets(context_name, safe=not unsafe)


def loqet_print_cli(
        loqet_name: str,
        context_name: str,
        to_json: bool = False,
        target: str = "default"
) -> None:
    """CLI for load_loqet, and print to terminal"""
    contents = read_loqet(loqet_name, context_name, target)
    if to_json:
        contents = json.dumps(yaml.safe_load(contents), indent=2)
    print(contents)


def loqet_view_cli(loqet_name: str, context_name: str, target: str = "default") -> None:
    """CLI for load_loqet, and view in page viewer"""
    content = read_loqet(loqet_name, context_name, target)
    if isinstance(content, str):
        pydoc.pager(content)
    else:
        print("No content to view")


def loqet_edit_cli(loqet_name: str, context_name: str, safe: bool) -> None:
    """Edit loqet encrypted loq config in place via $EDITOR"""
    loqet_names = list_loqets(context_name)
    if loqet_name not in loqet_names:
        print(f"{loqet_name} is not a loqet in the {context_name} context.")
        return

    loqet_filenames = list_loqet_filenames(loqet_name, context_name)
    base_filename = f"{loqet_name}.yaml"
    loq_filename = f"{loqet_name}.yaml.loq"
    open_filename = f"{loqet_name}.yaml.open"
    if loq_filename not in loqet_filenames:
        if open_filename in loqet_filenames or base_filename in loqet_filenames:
            encrypt_loqet(loqet_name, context_name, safe=safe)
        else:
            print(f"{loq_filename} not in loqet. "
                  f"Current {loqet_name} loqet files: {loqet_filenames}")
            return
    loqet_path, secret_key = get_context(context_name)
    loq_path = os.path.join(loqet_path, loq_filename)
    loq_edit_file(loq_path, secret_key, safe=safe)


def loqet_get_cli(namespace_path: str, context_name: str, target: str = "default") -> None:
    """CLI for loqet_get, and print to terminal as json"""
    loqet_contents = loqet_get(namespace_path, context_name, target)
    print(json.dumps(loqet_contents, indent=2))


def loqet_diff_cli(loqet_name: str, context_name: str) -> None:
    """
    Print diff of all configs for a single loqet
    (.loq, .open, and .yaml, if present)
    """
    diff = ""
    loqet_path, secret_key = get_context(context_name)
    loqet_filenames = list_loqet_filenames(loqet_name, context_name)
    if len(loqet_filenames) <= 1:
        print(f"No diff. Less than two files in {loqet_name} loqet: {loqet_filenames}")
    elif len(loqet_filenames) >= 2:
        pairs = set()
        for f1 in loqet_filenames:
            for f2 in loqet_filenames:
                ordered_pair = tuple(sorted([f1, f2]))
                if f1 != f2 and ordered_pair not in pairs:
                    pairs.add(ordered_pair)
        for pair in list(pairs):
            diff += "*" * os.get_terminal_size().columns + "\n"
            f1_path = os.path.join(loqet_path, pair[0])
            f2_path = os.path.join(loqet_path, pair[1])
            diff += loq_diff(f1_path, f2_path, secret_key)
    pydoc.pager(diff)


def loqet_find_cli(search_term: str, context_name: str) -> None:
    """Searches loqet context for all instances of search_term"""
    matches = []
    match_lines = {}
    loqet_path, secret_key = get_context(context_name)
    loqet_dir_filenames = list_loqet_dir(context_name)
    for filename in loqet_dir_filenames:
        file_path = os.path.join(loqet_path, filename)
        if filename.endswith(".loq"):
            file_contents = read_loq_file(file_path, secret_key)
        else:
            file_contents = read_file(file_path)
        for line_num, line in enumerate(file_contents.split("\n")):     # noqa
            if search_term in line:
                if filename not in matches:
                    matches.append(filename)
                if filename not in match_lines:
                    match_lines[filename] = {line_num: line}
                else:
                    match_lines[filename][line_num] = line

    print(f"Found {len(matches)} matching files in {loqet_path}:")
    for match in matches:
        print(f"{match}:")
        for line_num, line in match_lines[match].items():
            print(f"\t{str(line_num).ljust(4)}: {line}")


#########################
# Command Parser/Router #
#########################

def _get_target(args: argparse.Namespace) -> str:
    if args.loq and args.open:
        raise LoqetInvalidArgumentException("Can only pass one of --loq or --open")
    elif args.loq:
        target = "loq"
    elif args.open:
        target = "open"
    else:
        target = "default"
    return target


def loqet_parse_args() -> argparse.Namespace:
    """Generate argparser namespace for `loqet` command args"""
    parser = argparse.ArgumentParser(
        description="loqet command",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    subparser_setup(subparsers, loqet_commands)
    context_subparser = context_command_parser(subparsers)
    args = parser.parse_args()

    # "help" and blank cases use parser print_help function, so this
    # is clunky to do anywhere else
    if args.command in ["help", None]:
        parser.print_help()
        sys.exit()
    elif args.command == "context" and args.context_command in ["help", None]:
        context_subparser.print_help()
        sys.exit()

    return args


def loqet_command_router(args: argparse.Namespace) -> None:
    """Route `loqet` cli inputs to library calls"""
    # switch statements can't come soon enough
    if args.command == "context":
        context_command_router(args)
    else:
        try:
            _, secret_key = get_context(args.context)
        except LoqetNoSetContextException as e:
            print(e)
            print("Please set an active context with `loqet context set _` "
                  "or pass a context with `--context _`")
            print("Taking no action")
            return
        if args.command == "list":
            loqet_list_cli(args.context)
        elif args.command == "ls":
            loqet_ls_cli(args.context, args.paths)
        elif args.command == "create":
            loqet_create_cli(args.create_loqet_name, args.context)
        elif args.command == "encrypt":
            loqet_encrypt_cli(args.encrypt_loqet_name, args.context, safe=args.safe)
        elif args.command == "decrypt":
            loqet_decrypt_cli(args.decrypt_loqet_name, args.context, safe=args.safe)
        elif args.command == "close":
            loqet_close_cli(args.context, unsafe=args.unsafe)
        elif args.command == "open":
            loqet_open_cli(args.context, unsafe=args.unsafe)
        elif args.command == "print":
            target = _get_target(args)
            loqet_print_cli(
                args.print_loqet_name,
                args.context,
                to_json=args.json,
                target=target
            )
        elif args.command == "view":
            target = _get_target(args)
            loqet_view_cli(args.view_loqet_name, args.context, target)
        elif args.command == "edit":
            loqet_edit_cli(args.edit_loqet_name, args.context, safe=args.safe)
        elif args.command == "get":
            target = _get_target(args)
            loqet_get_cli(args.get_namespace_path, args.context, target)
        # elif args.command == "set":
        #     loqet_set()
        elif args.command == "diff":
            loqet_diff_cli(args.diff_loqet_name, args.context)
        elif args.command == "find":
            loqet_find_cli(args.find_search_term, args.context)


# Entry point for loqet command in setup.py
def loqet_cli() -> None:
    """Execute `loqet` command line interface."""
    args = loqet_parse_args()
    loqet_command_router(args)


if __name__ == "__main__":
    loqet_cli()
