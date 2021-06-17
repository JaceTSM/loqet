"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

---------------------------------------------------

Secret Store (loqet api)

Tools for interfacing with a loqet context, which acts as a
project-specific secret store.

Base Secret Store API:
list_loqets     get list of loqet names in a context
list_loqet_dir  list all files in loqet dir
loqet_load      load a single loqet namespace (one file from the loqet dir)


Notes:
* When a .loq and .open file exist for a given config,
    the .open file contents take read precedence. This way you
    can unloq a file, change it, test your change, and then
    loq it when you are done testing
* This isn't initially intended for dynamic secret setting
    within python. For now the api will be read-only so people
    don't accidentally overwrite their local secret stores without
    putting some effort in. :)
"""

import os
import yaml
from typing import List, Tuple, Union

from loqet.loqet_contexts import get_context
from loqet.encryption_suite import (
    loq_decrypt_file, loq_encrypt_file, load_loq_config,
    validate_loq_file, read_loq_file
)
from loqet.exceptions import LoqetInvalidArgumentException
from loqet.file_utils import read_file


# valid_extensions list also defines order of load precedence
VALID_EXTENSIONS = ["yaml.open", "yaml", "yaml.loq"]


#########################
# Precedence Management #
#########################

def list_loqet_filenames(loqet_name: str, context_name: str = None) -> List[str]:
    """
    List all valid config files for a loqet in a loqet context

    :param loqet_name:      name of loqet to list files for
    :param context_name:    loqet context to search in
    :return:                list of valid config files
    """
    loqet_dir, _ = get_context(context_name)
    matches = [
        f for f in os.listdir(loqet_dir)
        if f.partition(".")[0] == loqet_name
        and f.partition(".")[2] in VALID_EXTENSIONS
    ]
    return matches


def get_precedent_loqet_filename(loqet_name: str, context_name: str = None) -> str:
    """
    Returns filename of loqet file with highest precedence

    Loqets can have three different representations
    at any point in time: a yaml, yaml.open, or yaml.loq,
    with the following precedence:

    1. loqet_name.yaml.open
    2. loqet_name.yaml
    3. loqet_name.yaml.loq

    Loqets at lower precedence (lower on the list) are not loaded at all
    if an earlier loqet is loaded.

    :param loqet_name:      name of loqet to search
    :param context_name:    loqet context to search
    :return:                config file with the highest precedence
    """
    loqet_dir, _ = get_context(context_name)
    loqet_filenames = list_loqet_filenames(loqet_name, context_name)

    target_file = None
    for ext in VALID_EXTENSIONS:
        loqet_filename = f"{loqet_name}.{ext}"
        if loqet_filename in loqet_filenames:
            target_file = loqet_filename
            break

    return target_file


#######################
# Load Loqet Contents #
#######################


def read_loqet(
        loqet_name: str,
        context_name: str = None,
        target: str = "default"
) -> str:
    """
    Read highest precedence loqet file as a string.

    :param loqet_name:      name of loqet to load
    :param context_name:    loqet context to find named loqet in
    :param target:          [option: default, loq, open]
                            default - read highest precedence file
                            loq/open - target loq or open file
    :return:                [str] unencrypted loqet contents
    """
    loqet_dir, secret_key = get_context(context_name)

    if target == "default":
        precedent_config = get_precedent_loqet_filename(loqet_name, context_name)
        target_path = os.path.join(loqet_dir, precedent_config) \
            if precedent_config else None
    elif target in ["loq", "open"]:
        target_path = os.path.join(loqet_dir, f"{loqet_name}.yaml.{target}")
    else:
        raise LoqetInvalidArgumentException("target must be in [default, loq, open]")

    if target_path is None:
        contents = ""
    elif validate_loq_file(target_path):
        contents = read_loq_file(target_path, secret_key)
    else:
        contents = read_file(target_path)
    return contents


def load_loqet(loqet_name: str, context_name: str = None, target: str = "default") -> dict:
    """
    Load highest precedence loqet file as a dict.

    :param loqet_name:      name of loqet to load
    :param context_name:    loqet context to find named loqet in
    :param target:          [option: default, loq, open]
                            default - read highest precedence file
                            loq/open - target loq or open file
    :return:                [dict] unencrypted loqet contents
    """
    loqet_contents = read_loqet(loqet_name, context_name, target)
    if loqet_contents:
        config = yaml.safe_load(loqet_contents)
    else:
        config = {}
    return config


####################
# Loqet Management #
####################

def list_loqets(context_name: str = None) -> List[str]:
    """
    Returns list of loqet names in context

    :param context_name:    loqet context to list
    :return:                list of loqet names
    """
    loqet_files = list_loqet_dir(context_name)
    loqet_base_names = [
        f.partition(".")[0]
        for f in loqet_files
        if not f.startswith(".")
    ]
    return sorted(list(set(loqet_base_names)))


def list_loqet_dir(
        context_name: str = None,
        full_paths: bool = False
) -> List[str]:
    """
    Returns all filenames in loqet dir

    :param context_name:    loqet context to list
    :param full_paths:      Return list of full paths rather than filenames
    :return:                list of files in loqet context dir
    """
    loqet_dir, _ = get_context(context_name)
    if full_paths:
        dir_contents = [
            os.path.join(loqet_dir, item)
            for item in os.listdir(loqet_dir)
        ]
    else:
        dir_contents = os.listdir(loqet_dir)
    return dir_contents


def create_loqet(loqet_name: str, context_name: str = None) -> Union[str, None]:
    """
    Create a loqet namespace in a loqet context

    :param loqet_name:      Name of loqet namespace to create
    :param context_name:    Name of context to create loqet namespace in
    :return:                [str/None] .open file name
    """
    loqet_dir, _ = get_context(context_name)
    loqet_names = list_loqets(context_name)
    if loqet_name in loqet_names:
        loqet_path = None
    else:
        loqet_path = os.path.join(loqet_dir, f"{loqet_name}.yaml.open")
        with open(loqet_path, "w") as _:
            # creates empty file
            pass
    return loqet_path


def encrypt_loqet(
        loqet_name: str,
        context_name: str = None,
        safe: bool = False
) -> Union[str, None]:
    """
    Encrypt open config file for a loqet namespace

    :param loqet_name:      Name of loqet to encrypt
    :param context_name:    Name of context to check for loqet
    :param safe:            If True, make backup of loq file and update gitignore
    :return:                [str/None] encrypted file path
    """
    loqet_dir, secret_key = get_context(context_name)
    loqet_files = list_loqet_dir(context_name)
    open_filename = f"{loqet_name}.yaml.open"
    base_filename = f"{loqet_name}.yaml"
    if base_filename in loqet_files and open_filename in loqet_files:
        print(f"WARN - both {base_filename} and {open_filename} exist, ignoring {base_filename}")
    if open_filename in loqet_files:
        open_path = os.path.join(loqet_dir, open_filename)
        loq_path = loq_encrypt_file(open_path, secret_key, safe=safe)
    elif base_filename in loqet_files:
        base_path = os.path.join(loqet_dir, open_filename)
        loq_path = loq_encrypt_file(base_path, secret_key, safe=safe)
    else:
        print(f"WARN - No loqet named {loqet_name} in {loqet_dir}")
        loq_path = None
    return loq_path


def decrypt_loqet(
        loqet_name: str,
        context_name: str = None,
        safe: bool = False
) -> Union[str, None]:
    """
    Decrypt encrypted config file for a loqet namespace

    :param loqet_name:      Name of loqet to decrypt
    :param context_name:    Name of context to check for loqet
    :param safe:            If True, make backup of open file and update gitignore
    :return:                [bool] Success
    """
    loqet_dir, secret_key = get_context(context_name)
    loqet_files = list_loqet_dir(context_name)
    loqet_filename = f"{loqet_name}.yaml.loq"
    if loqet_filename in loqet_files:
        loq_path = os.path.join(loqet_dir, loqet_filename)
        open_path = loq_decrypt_file(loq_path, secret_key, safe=safe)
    else:
        print(f"WARN - No loqet named {loqet_name} in {loqet_dir}")
        open_path = None
    return open_path


def close_loqets(context_name: str = None, safe: bool = True) -> List[Tuple[str, str]]:
    """
    Encrypts all .open files in named loqet context

    Does not loq base files (files without .open extension).
    """
    loqet_names = list_loqets(context_name)
    successes = []
    for loqet_name in loqet_names:
        success = encrypt_loqet(loqet_name, context_name, safe=safe)
        successes.append(success)
    return list(zip(loqet_names, successes))


def open_loqets(context_name: str = None, safe: bool = True) -> List[Tuple[str, str]]:
    """
    Decrypt all loq_config files in named loqet

    Will create/update .gitignore and make .bak files
    if safe is True (default:true)
    """
    loqet_names = list_loqets(context_name)
    successes = []
    for loqet_name in loqet_names:
        success = decrypt_loqet(loqet_name, context_name, safe=safe)
        successes.append(success)
    return list(zip(loqet_names, successes))


def loqet_get(
        loqet_namespace_path: str,
        context_name: str = None,
        target: str = "default"
) -> Union[str, dict]:
    """
    Get contents of loqet config at dot-delimited namespace path.

    eg:
        loqet_get("loqet_name.path.to.config")

    Notes:
    * Invalid paths return empty dict
    * lists can be accessed via numeric index
        eg. loqet_get("loqet_name.path.to.list.0.foo")

    :param loqet_namespace_path:
        dot delimited path to desired config, prefixed
        by namespace (loqet name)
    :param context_name:
        loqet context to search for loqet namespace
    :param target:
        [option: default, loq, open]
        default - read highest precedence file
        loq/open - target loq or open file
    :return:
        contents of loqet at target path. Dict if not at
        leaf node, string at leaves, and empty dict if nothing
        at the target path.
    """
    loqet_name, _, namespace_path = loqet_namespace_path.partition(".")
    loqet_contents = load_loqet(loqet_name, context_name, target)
    if namespace_path:
        for key in namespace_path.split("."):
            if isinstance(loqet_contents, list):
                try:
                    loqet_contents = loqet_contents[int(key)]
                except (TypeError, IndexError, ValueError):
                    loqet_contents = {}
            elif isinstance(loqet_contents, dict):
                loqet_contents = loqet_contents.get(key, {})
            else:
                loqet_contents = {}
    return loqet_contents


def loqet_set(loqet_namespace_path: str, context_name: str = None):  # noqa
    """
    We don't support direct setting loqet config values via CLI or API because
    it would be an opaque process, and if used in automation could lead to
    scenarios where secrets are unintentionally overwritten and lost.
    If you want to change a secret in an encrypted loqet, use `loqet edit`
    or `loqet decrypt` and `loqet encrypt`.
    """
    raise NotImplementedError()
