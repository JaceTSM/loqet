"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""

import argparse
import json

from loqet.loqet_contexts import (
    create_loqet_context, get_active_context_name, get_loqet_contexts,
    get_context_info, set_loqet_context, unset_loqet_context
)
from loqet.cli_utils import subparser_setup


context_commands = {
    "help": {
        "help": "Print out loqet context command help",
        "subparser_args": [],
    },
    "init": {
        "help": "Initialize a loqet context",
        "subparser_args": [
            "context_init_name",
            "context_init_dir",
        ],
    },
    "get": {
        "help": "Get the active context name",
        "subparser_args": [],
    },
    "list": {
        "help": "List the set of contexts",
        "subparser_args": [],
    },
    "info": {
        "help": "Get detailed info about a context",
        "subparser_args": ["--context"],
    },
    "set": {
        "help": "Set the active context",
        "subparser_args": ["context_set_name"],
    },
    "unset": {
        "help": "Unset the active context",
        "subparser_args": [],
    },
}


#####################
# Loqet Context CLI #
#####################

# loqet context init <context_name> <target_directory> [secret_key]
def loqet_context_init_cli(context_name: str, context_dir: str) -> None:
    """CLI for create_loqet_context"""
    create_loqet_context(context_name, context_dir)
    context_info = get_context_info(context_name)
    print(f"Loqet context {context_name} "
          f"created at {context_info.get('loqet_dir', 'UNKNOWN_LOQET_DIR')} "
          f"with keyfile {context_info.get('keyfile', 'UNKNOWN_KEYFILE')}")


# loqet context get
def loqet_context_get_cli() -> None:
    """CLI for get_active_context_name"""
    context_name = get_active_context_name()
    if context_name:
        print(context_name)
    else:
        print("No active loqet context")


# loqet context list
def loqet_context_list_cli() -> None:
    """CLI for get_loqet_contexts"""
    contexts = get_loqet_contexts()
    active_context = get_active_context_name()
    if not contexts:
        print("No loqet contexts have been created. "
              "Create one with 'loqet init <context_name> <target_loqet_directory>'")
        return
    print("Loqet contexts:")
    longest_context = len(max(contexts.keys(), key=len))
    for context_name, context in contexts.items():
        prefix = "*" if context_name == active_context else " "
        print(f"{prefix} {context_name.ljust(longest_context + 1)}: "
              f"{context['loqet_dir']}")


# loqet context info
def loqet_context_info_cli(context_name: str = None) -> None:
    """CLI for get_context_info"""
    context_info = get_context_info(context_name)
    if context_info:
        print(json.dumps(context_info, indent=2))
    else:
        if context_name:
            print(f"{context_name} context not found. "
                  f"Run 'loqet context list' to see all contexts")
        else:
            print("No context provided (--context) and no active context.")


# loqet context set
def loqet_context_set_cli(context_name: str) -> None:
    """CLI for set_loqet_context"""
    success = set_loqet_context(context_name)
    if success:
        print(f"Set active context to {context_name}")
    else:
        print(f"Failed to set active context to '{context_name}'. "
              f"Run 'loqet context list' to see available contexts.")


# loqet context unset
def loqet_context_unset_cli() -> None:
    """CLI for unset_loqet_context"""
    active_context = get_active_context_name()
    if active_context:
        unset_loqet_context()
        print(f"Unset active loqet context.")
    else:
        print("No active context set.")


#########################
# Command Parser/Router #
#########################

# type hints???
def context_command_parser(subparsers):
    """
    Add `loqet context` sub-command subparser to top
    level `loqet` command
    """
    context_parser = subparsers.add_parser("context")
    sub_subparsers = context_parser.add_subparsers(
        dest="context_command",
        help="Context sub-command help"
    )
    subparser_setup(sub_subparsers, context_commands)
    return context_parser


def context_command_router(args: argparse.Namespace) -> None:
    """Route `loqet context` cli inputs to library calls"""
    if args.context_command == "init":
        loqet_context_init_cli(
            context_name=args.context_init_name,
            context_dir=args.context_init_dir
        )
    elif args.context_command == "get":
        loqet_context_get_cli()
    elif args.context_command == "info":
        loqet_context_info_cli(args.context)
    elif args.context_command == "set":
        loqet_context_set_cli(args.context_set_name)
    elif args.context_command == "unset":
        loqet_context_unset_cli()
    elif args.context_command == "list":
        loqet_context_list_cli()
