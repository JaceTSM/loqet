"""
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
from typing import List, Tuple

from loqet.loqet_contexts import get_context
from loqet.encryption_suite import (
    loq_decrypt_file, loq_encrypt_file, read_loq_file
)


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

def load_loqet(loqet_name: str, context_name: str = None) -> dict:
    """
    Load highest precedence loqet file as a dict.

    :param loqet_name:      name of loqet to load
    :param context_name:    loqet context to find named loqet in
    :return:                [dict] unencrypted loqet contents
    """
    loqet_filename = get_precedent_loqet_filename(loqet_name, context_name)
    if not loqet_filename:
        return {}
    if loqet_filename.endswith(".loq"):
        loqet_contents = load_loq_config(loqet_filename, context_name)
    else:
        loqet_contents = yaml.safe_load(loqet_filename)
    return loqet_contents


def load_loq_config(loq_path: str, secret_key: bytes) -> dict:
    """
    Decrypts a vaulted config file and loads it as dict.

    :param loq_path:        name of loqet to load
    :param secret_key:      secret key to decrypt loq file
    :return:                [dict] unencrypted loqet contents
    """
    loq_contents = read_loq_file(loq_path, secret_key)
    config = yaml.safe_load(loq_contents)
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
    ]
    return sorted(list(set(loqet_base_names)))


def list_loqet_dir(context_name: str = None) -> List[str]:
    """
    Returns all filenames in loqet dir

    :param context_name:    loqet context to list
    :return:                list of files in loqet context dir
    """
    loqet_dir, _ = get_context(context_name)
    return os.listdir(loqet_dir)


def create_loqet(loqet_name: str, context_name: str = None) -> bool:
    """
    Create a loqet namespace in a loqet context

    :param loqet_name:      Name of loqet namespace to create
    :param context_name:    Name of context to create loqet namespace in
    :return:                [bool] success
    """
    loqet_dir, _ = get_context(context_name)
    loqet_names = list_loqets(context_name)
    if loqet_name in loqet_names:
        success = False
    else:
        loqet_path = os.path.join(loqet_dir, f"{loqet_name}.yaml.open")
        with open(loqet_path, "w") as _:
            # creates empty file
            pass
        success = True
    return success


def encrypt_loqet(loqet_name: str, context_name: str = None, safe: bool = False) -> bool:
    """
    Encrypt open config file for a loqet namespace

    :param loqet_name:      Name of loqet to encrypt
    :param context_name:    Name of context to check for loqet
    :param safe:            If True, make backup of loq file and update gitignore
    :return:                [bool] Success
    """
    loqet_dir, secret_key = get_context(context_name)
    loqet_files = list_loqet_dir(context_name)
    open_filename = f"{loqet_name}.yaml.open"
    base_filename = f"{loqet_name}.yaml"
    if base_filename in loqet_files and open_filename in loqet_files:
        print(f"WARN - both {base_filename} and {open_filename} exist, ignoring {base_filename}")
    if open_filename in loqet_files:
        open_path = os.path.join(loqet_dir, open_filename)
        loq_encrypt_file(open_path, secret_key, safe=safe)
        success = True
    elif base_filename in loqet_files:
        base_path = os.path.join(loqet_dir, open_filename)
        loq_encrypt_file(base_path, secret_key, safe=safe)
        success = True
    else:
        print(f"WARN - No loqet named {loqet_name} in {loqet_dir}")
        success = False
    return success


def decrypt_loqet(loqet_name: str, context_name: str = None, safe: bool = False) -> bool:
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
        loq_decrypt_file(loq_path, secret_key, safe=safe)
        success = True
    else:
        print(f"WARN - No loqet named {loqet_name} in {loqet_dir}")
        success = False
    return success


def close_loqets(context_name: str = None, safe: bool = True) -> List[Tuple[str, bool]]:
    """
    Encrypts all .open files in named loqet

    Does not loq base files (files without .open extension).
    """
    loqet_names = list_loqets(context_name)
    successes = []
    for loqet_name in loqet_names:
        success = encrypt_loqet(loqet_name, context_name, safe=safe)
        successes.append(success)
    return list(zip(loqet_names, successes))


def open_loqets(context_name: str = None, safe: bool = True) -> List[Tuple[str, bool]]:
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


def loqet_get(loqet_namespace_path: str, context_name: str = None) -> dict:
    """
    Get contents of loqet config at dot-delimited namespace path

    eg:
        loqet_get("loqet_name.path.to.config")

    :param loqet_namespace_path:
        dot delimited path to desired config, prefixed
        by namespace (loqet name)
    :param context_name:
        loqet context to search for loqet namespace
    :return:
        contents of loqet at target path. Dict if not at
        leaf node, string at leaves, and empty dict if nothing
        at the target path.
    """
    loqet_name, _, namespace_path = loqet_namespace_path.partition(".")
    loqet_contents = load_loqet(loqet_name, context_name)
    for key in namespace_path.split("."):
        if isinstance(loqet_contents, dict):
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
