import argparse
import os
import sys

pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)

from loqet.secret_store import (
    list_loqets, list_loqet_dir, create_loqet, encrypt_loqet, decrypt_loqet,
    close_loqets, open_loqets, print_loqet, view_loqet, edit_loqet, loqet_get,
    loqet_diff, loqet_find
)   # noqa
from loqet.loqet_contexts import get_context    # noqa


commands = {
    "list": {
        "help": "",
        "subparser_args": [],
    },
    "ls": {
        "help": "",
        "subparser_args": [],
    },
    "create": {
        "help": "",
        "subparser_args": ["create_loqet_name"],
    },
    "encrypt": {
        "help": "",
        "subparser_args": ["encrypt_loqet_name"],
    },
    "decrypt": {
        "help": "",
        "subparser_args": ["decrypt_loqet_name"],
    },
    "close": {
        "help": "",
        "subparser_args": [],
    },
    "open": {
        "help": "",
        "subparser_args": [],
    },
    "print": {
        "help": "",
        "subparser_args": ["print_loqet_name"],
    },
    "view": {
        "help": "",
        "subparser_args": ["view_loqet_name"],
    },
    "edit": {
        "help": "",
        "subparser_args": ["edit_loqet_name"],
    },
    "get": {
        "help": "",
        "subparser_args": ["get_namespace_path"],
    },
    # # NOT YET SUPPORTED
    # "set": {
    #     "help": "",
    #     "subparser_args": [],
    # },
    "diff": {
        "help": "",
        "subparser_args": ["diff_loqet_name"],
    },
    "find": {
        "help": "",
        "subparser_args": ["find_search_term"],
    },
}


def loqet_parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--safe", action="store_true")
    parser.add_argument("--context", help="")
    subparsers = parser.add_subparsers(help="Sub-command help", dest="command")

    for command, command_config in commands.items():
        iter_subparser = subparsers.add_parser(command, help=command_config.get("help"))
        for subparser_arg in command_config.get("subparser_args", []):
            iter_subparser.add_argument(subparser_arg)

    args = parser.parse_args()
    return args


def loqet_command_router(args):
    _, secret_key = get_context(args.context)
    if args.command == "list":
        list_loqets(args.context)
    elif args.command == "ls":
        list_loqet_dir(args.context)
    elif args.command == "create":
        create_loqet(args.create_loqet_name, args.context)
    elif args.command == "encrypt":
        encrypt_loqet(args.encrypt_loqet_name, args.context, safe=args.safe)
    elif args.command == "decrypt":
        decrypt_loqet(args.decrypt_loqet_name, args.context, safe=args.safe)
    elif args.command == "close":
        close_loqets(args.context, safe=args.safe)
    elif args.command == "open":
        open_loqets(args.context, safe=args.safe)
    elif args.command == "print":
        print_loqet(args.print_loqet_name, args.context)
    elif args.command == "view":
        view_loqet(args.view_loqet_name, args.context)
    elif args.command == "edit":
        edit_loqet(args.edit_loqet_name, args.context, safe=args.safe)
    elif args.command == "get":
        loqet_get(args.get_namespace_path, args.context)
    # elif args.command == "set":
    #     loqet_set()
    elif args.command == "diff":
        loqet_diff(args.diff_loqet_name, args.context)
    elif args.command == "find":
        loqet_find(args.find_search_term, args.context)


# Entry point for loq command in setup.py
def loqet_cli():
    args = loqet_parse_args()
    loqet_command_router(args)


if __name__ == "__main__":
    loqet_cli()
