# SAFE_ARG/UNSAFE_ARG are shortcuts for `--safe`
# and `--unsafe` boolean subparser args
SAFE_ARG = {
    "args": ["--safe"],
    "kwargs": {
        "action": "store_true",
    },
}

UNSAFE_ARG = {
    "args": ["--unsafe"],
    "kwargs": {
        "action": "store_true",
    },
}


def subparser_setup(subparser_list, command_dict):
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
