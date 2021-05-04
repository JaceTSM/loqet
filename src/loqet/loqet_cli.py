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
from loqet.loqet_contexts import (
    create_loqet_context, get_active_context_name, get_context_info,
    set_loqet_context, unset_loqet_context, list_loqet_contexts, get_context
)    # noqa
from loqet.cli_utils import SAFE_ARG, UNSAFE_ARG, subparser_setup   # noqa


loqet_commands = {
    "list": {
        "help": "",
        "subparser_args": ["--context"],
    },
    "ls": {
        "help": "",
        "subparser_args": ["--context"],
    },
    "create": {
        "help": "",
        "subparser_args": [
            "create_loqet_name",
            "--context",
        ],
    },
    "encrypt": {
        "help": "",
        "subparser_args": [
            "encrypt_loqet_name",
            "--context",
            SAFE_ARG,
        ],
    },
    "decrypt": {
        "help": "",
        "subparser_args": [
            "decrypt_loqet_name",
            "--context",
            SAFE_ARG,
        ],
    },
    "close": {
        "help": "",
        "subparser_args": [
            "--context",
            UNSAFE_ARG,
        ],
    },
    "open": {
        "help": "",
        "subparser_args": [
            "--context",
            UNSAFE_ARG,
        ],
    },
    "print": {
        "help": "",
        "subparser_args": [
            "print_loqet_name",
            "--context",
        ],
    },
    "view": {
        "help": "",
        "subparser_args": [
            "view_loqet_name",
            "--context",
        ],
    },
    "edit": {
        "help": "",
        "subparser_args": [
            "edit_loqet_name",
            "--context",
            SAFE_ARG,
        ],
    },
    "get": {
        "help": "",
        "subparser_args": [
            "get_namespace_path",
            "--context",
        ],
    },
    # # NOT YET SUPPORTED
    # "set": {
    #     "help": "",
    #     "subparser_args": [],
    # },
    "diff": {
        "help": "",
        "subparser_args": [
            "diff_loqet_name",
            "--context",
        ],
    },
    "find": {
        "help": "",
        "subparser_args": [
            "find_search_term",
            "--context",
        ],
    },
}

context_commands = {
    "init": {
        "help": "",
        "subparser_args": [
            "context_init_name",
            "context_init_dir",
            "--secret-key"
        ],
    },
    "get": {
        "help": "",
        "subparser_args": [],
    },
    "list": {
        "help": "",
        "subparser_args": [],
    },
    "info": {
        "help": "",
        "subparser_args": ["--context"],
    },
    "set": {
        "help": "",
        "subparser_args": ["context_set_name"],
    },
    "unset": {
        "help": "",
        "subparser_args": [],
    },
}


def context_command_parser(subparsers):
    context_parser = subparsers.add_parser("context")
    sub_subparsers = context_parser.add_subparsers(
        dest="context_command",
        help="Context sub-command help"
    )
    subparser_setup(sub_subparsers, context_commands)


def loqet_parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    subparser_setup(subparsers, loqet_commands)
    context_command_parser(subparsers)
    args = parser.parse_args()
    return args


def context_command_router(args):
    if args.context_command == "init":
        create_loqet_context(
            context_name=args.context_init_name,
            loqet_dir=args.context_init_dir,
            secret_key=args.secret_key
        )
    elif args.context_command == "get":
        get_active_context_name()
    elif args.context_command == "info":
        get_context_info(args.context)
    elif args.context_command == "set":
        set_loqet_context(args.context)
    elif args.context_command == "unset":
        unset_loqet_context()
    elif args.context_command == "list":
        list_loqet_contexts()


def loqet_command_router(args):
    # switch statements can't come soon enough
    if args.command == "context":
        context_command_router(args)
    else:
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
            close_loqets(args.context, safe=not args.unsafe)
        elif args.command == "open":
            open_loqets(args.context, safe=not args.unsafe)
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
    print(args)
    # loqet_command_router(args)


if __name__ == "__main__":
    loqet_cli()
