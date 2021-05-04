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
