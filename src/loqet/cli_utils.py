"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""

# SAFE_ARG/UNSAFE_ARG are shortcuts for `--safe`
# and `--unsafe` boolean subparser args.
# Use --safe for commands that should default to "unsafe"
SAFE_ARG = {
    "args": ["--safe"],
    "kwargs": {
        "action": "store_true",
    },
}

# Use --unsafe for commands that should default to "safe"
UNSAFE_ARG = {
    "args": ["--unsafe"],
    "kwargs": {
        "action": "store_true",
    },
}

LOQ_ARG = {
    "args": ["--loq"],
    "kwargs": {
        "action": "store_true",
        "help": "target .loq file"
    },
}

OPEN_ARG = {
    "args": ["--open"],
    "kwargs": {
        "action": "store_true",
        "help": "target .open file"
    },
}


def subparser_setup(subparser_list, command_dict: dict) -> None:
    """
    Add set of subparser commands to a subparser list.

    :param subparser_list:
        output of argparse.ArgumentParser().add_subparsers

    :param command_dict:
        eg:
        commands = {
            "command_name": {
                "help": "Command help string",
                "subparser_args": [
                    "named_arg",
                    {
                        "args": ["--boolean-arg"],
                        "kwargs": {"action": "store_true"}
                    },
                ],
            },
            ...
        }

    :return: n/a - we only care about side effects :scream:
    """
    for command, command_config in command_dict.items():
        command_subparser = subparser_list.add_parser(
            command, help=command_config.get("help")
        )
        for subparser_arg in command_config.get("subparser_args", []):
            if isinstance(subparser_arg, dict):
                command_subparser.add_argument(
                    *subparser_arg["args"],
                    **subparser_arg["kwargs"]
                )
            else:
                command_subparser.add_argument(subparser_arg)
