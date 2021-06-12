"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""

import os
import shutil
import time
from typing import Union

from loqet.loqet_configs import SAFE_MODE


def backup_file(filename: str) -> None:
    """
    Create a copy of a file with a .bak.<timestamp>

    :param filename:    File path to back up
    :return:            n/a
    """
    if SAFE_MODE:
        update_gitignore(filename)
    backup_filename = f"{filename}.bak.{int(time.time())}"
    shutil.copyfile(filename, backup_filename)
    print(f"Backed up old {filename} to {backup_filename}")


def update_gitignore(filename: str) -> None:
    """
    Updates .gitignore at either directory of filename or
    at LOQET_GITIGNORE with .open/.bak extensions

    :param filename:    Target file to place .gitignore next to
    :return:            n/a
    """
    gitignore_entries = [
        "*.open*",
        "*.bak.*"
    ]
    if os.path.isdir(filename):
        target_dir = os.path.realpath(filename)
    else:
        target_dir = os.path.dirname(os.path.realpath(filename))
    default_gitignore_file = os.path.join(target_dir, ".gitignore")
    gitignore_file = os.environ.get("LOQET_GITIGNORE", default_gitignore_file)
    gitignore_file = (
        gitignore_file
        if gitignore_file.endswith(".gitignore")
        else default_gitignore_file
    )
    with open(gitignore_file, "a+") as f:
        f.seek(0)
        contents = f.read()
        for entry in gitignore_entries:
            if entry not in contents:
                if len(contents) > 0:
                    f.write("\n")
                f.write(f"{entry}\n")


def read_file(filename: str) -> str:
    """Read contents of file as string"""
    with open(filename, "r") as f:
        contents = f.read()
    return contents


def write_file(contents: Union[str, bytes], filename: str) -> None:
    """Write string or bytes to file"""
    if isinstance(contents, bytes):
        write_mode = "wb"
    else:
        write_mode = "w"
    with open(filename, write_mode) as f:
        f.write(contents)
