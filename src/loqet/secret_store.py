"""
Secret Store (loqet api)

Tools for interfacing with a loqet context, which acts as a
project-specific secret store.

Base Secret Store API:
list_loqets     get list of loqet names in a context
list_loqet_dir  list all files in loqet dir
loqet_load      load a single loqet namespace (one file from the loqet dir)

CLI:
loqet list      list loqet namespaces
loqet ls        list files in loqet dir
loqet create    create a loqet namespace
loqet encrypt   encrypt a single loqet namespace
loqet decrypt   decrypt a single loqet namespace
loqet close     encrypt all open files in loqet dir
loqet open      decrypt all loq files in loqet dir
loqet print     print contents of loqet namespace
loqet view      read contents of target loquet namespace in viewer (.loq file)
loqet edit      edit loqet namespace in editor (modifies .loq file only)
loqet get       print value from a loqet namespace (pass dot delimited path)
loqet set     **Not yet supported
loqet diff      determine where loq and open files differ
loqet find      search loqets for text (keys and values)


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
import pydoc
import yaml

from loqet.loqet_contexts import get_context
from loqet.encryption_suite import (
    loq_decrypt_file, loq_encrypt_file, read_loq_file,
    loq_edit_file, loq_diff
)
from loqet.utilities import read_file


# valid_extensions list also defines order of load precedence
VALID_EXTENSIONS = ["yaml.open", "yaml", "yaml.loq"]


#########################
# Precedence Management #
#########################

def list_loqet_filenames(loqet_name, context_name=None):
    loqet_dir, _ = get_context(context_name)
    matches = [
        f for f in os.listdir(loqet_dir)
        if f.partition(".")[0] == loqet_name
        and f.partition(".")[2] in VALID_EXTENSIONS
    ]
    return matches


def get_precedent_loqet_filename(loqet_name, context_name=None):
    """
    Returns filename of loqet file with highest precedence

    Loqets can have three different representations
    at any point in time: a yaml, yaml.open, or yaml.loq,
    with the following precedence:

    1. loqet_name.yaml.open
    2. loqet_name.yaml
    3. loqet_name.yaml.loq

    Loqets at lower precedence (lower on the list) are not loaded at all
    if an earlier loquet is loaded.
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

def load_loqet(loqet_name, context_name=None):
    """
    Load highest precedence loqet file as a dict.
    """
    loqet_filename = get_precedent_loqet_filename(loqet_name, context_name)
    if loqet_filename.endswith(".loq"):
        loqet_contents = load_loq_config(loqet_filename, context_name)
    else:
        loqet_contents = yaml.safe_load(loqet_filename)
    return loqet_contents


def load_loq_config(loq_path, secret_key):
    """Decrypts a vaulted config file and loads it as yaml"""
    loq_contents = read_loq_file(loq_path, secret_key)
    config = yaml.safe_load(loq_contents)
    return config


####################
# Loqet Management #
####################

# loqet list
def list_loqets(context_name=None):
    """Returns list of loqet names in context"""
    loquet_files = list_loqet_dir(context_name)
    loqet_base_names = [
        f.partition(".")[0]
        for f in loquet_files
    ]
    return sorted(list(set(loqet_base_names)))


# loqet ls
def list_loqet_dir(context_name=None):
    """Returns all filenames in loqet dir"""
    loqet_dir, _ = get_context(context_name)
    return os.listdir(loqet_dir)


# loqet create <loqet_name>
def create_loqet(loqet_name, context_name=None):
    loqet_dir, _ = get_context(context_name)
    loqet_names = list_loqets(context_name)
    if loqet_name in loqet_names:
        print(f"{loqet_name} loqet already exists in {loqet_dir}")
    else:
        loqet_path = os.path.join(loqet_dir, f"{loqet_name}.yaml.open")
        with open(loqet_path, "w") as _:
            # creates empty file
            pass


# loqet encrypt <loqet_name>
def encrypt_loqet(loqet_name, context_name=None, safe=False):
    loqet_dir, secret_key = get_context(context_name)
    loqet_files = list_loqet_dir(context_name)
    open_filename = f"{loqet_name}.yaml.open"
    base_filename = f"{loqet_name}.yaml"
    if base_filename in loqet_files and open_filename in loqet_files:
        print(f"WARN - both {base_filename} and {open_filename} exist, ignoring {base_filename}")
    if open_filename in loqet_files:
        open_path = os.path.join(loqet_dir, open_filename)
        loq_encrypt_file(open_path, secret_key, safe=safe)
    elif base_filename in loqet_files:
        base_path = os.path.join(loqet_dir, open_filename)
        loq_encrypt_file(base_path, secret_key, safe=safe)
    else:
        print(f"WARN - No loqet named {loqet_name} in {loqet_dir}")


# loqet decrypt <loqet_name>
def decrypt_loqet(loqet_name, context_name=None, safe=False):
    loqet_dir, secret_key = get_context(context_name)
    loqet_files = list_loqet_dir(context_name)
    loqet_filename = f"{loqet_name}.yaml.loq"
    if loqet_filename in loqet_files:
        loq_path = os.path.join(loqet_dir, loqet_filename)
        loq_decrypt_file(loq_path, secret_key, safe=safe)
    else:
        print(f"WARN - No loqet named {loqet_name} in {loqet_dir}")


# loqet close all
def close_loqets(context_name=None, safe=True):
    """
    Encrypts all .open files in named loqet

    Does not loq base files (files without .open extension).
    """
    loqet_names = list_loqets(context_name)
    for loqet_name in loqet_names:
        encrypt_loqet(loqet_name, context_name, safe=safe)


# loqet open
def open_loqets(context_name=None, safe=True):
    """
    Decrypt all loq_config files in named loqet

    Will create/update .gitignore and make .bak files
    if safe is True (default:true)
    """
    loqet_names = list_loqets(context_name)
    for loqet_name in loqet_names:
        decrypt_loqet(loqet_name, context_name, safe=safe)


# loqet print <loqet_name>
def print_loqet(loqet_name, context_name=None):
    print(load_loqet(loqet_name, context_name))


# loqet view <loqet_name>
def view_loqet(loqet_name, context_name=None):
    content = load_loqet(loqet_name, context_name)
    pydoc.pager(content)


# loqet edit <loqet_name>
def edit_loqet(loqet_name, context_name=None, safe=False):
    loqet_filenames = list_loqet_filenames(loqet_name, context_name)
    loq_filename = f"{loqet_name}.yaml.loq"
    if loq_filename not in loqet_filenames:
        print(f"{loq_filename} not in loqet. "
              f"Current {loqet_name} loqet files: {loqet_filenames}")
    else:
        loqet_path, secret_key = get_context(context_name)
        loq_path = os.path.join(loqet_path, loq_filename)
        loq_edit_file(loq_path, secret_key, safe=safe)


# loqet get <loqet_name.path.to.config>
def loqet_get(loqet_namespace_path, context_name=None):
    """
    eg:
        loqet_get("loqet_name.path.to.config")

    :param loqet_namespace_path:
        dot delimited path to desired config, prefixed
        by namespace (loqet name)
    :param context_name:
    :return:
        contents of loqet at target path. Dict if not at
        leaf node, string at leaves, and empty dict if nothing
        at the target path.
    """
    loqet_name, _, namespace_path = loqet_namespace_path.partition(".")
    loqet_contents = load_loqet(loqet_name, context_name)
    for key in namespace_path.split("."):
        loqet_contents = loqet_contents.get(key, {})
    return loqet_contents


# loqet set
def loqet_set(loqet_namespace_path, context_name=None):  # noqa
    raise NotImplementedError()


# loqet diff
def loqet_diff(loqet_name, context_name=None):
    loqet_path, secret_key = get_context(context_name)
    loqet_filenames = list_loqet_filenames(loqet_name, context_name)
    if len(loqet_filenames) <= 1:
        print(f"No diff. Less than two files in {loqet_name} loqet: {loqet_filenames}")
    else:
        for f1 in loqet_filenames:
            for f2 in loqet_filenames:
                if f1 != f2:
                    f1_path = os.path.join(loqet_path, f1)
                    f2_path = os.path.join(loqet_path, f2)
                    loq_diff(f1_path, f2_path, secret_key)
                    print("*" * os.get_terminal_size().columns)


# loqet find
def loqet_find(search_term, context_name=None):
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
        for line_num, line in file_contents.split("\n"):
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
