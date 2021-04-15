import os
import shutil
import time

from src.loqet.loqet_configs import SAFE_MODE


def backup_file(filename):
    if SAFE_MODE:
        update_gitignore(filename)
    shutil.copyfile(filename, f"{filename}.bak.{int(time.time())}")


def update_gitignore(filename):
    """
    Updates .gitignore at either directory of filename or
    at LOQET_GITIGNORE with .open/.bak extensions
    """
    gitignore_entries = [
        "*.open*"
        "*.bak.*"
    ]

    target_dir = os.path.dirname(os.path.realpath(filename))
    default_gitignore_file = os.path.join(target_dir, ".gitignore")
    gitignore_file = os.environ.get("LOQET_GITIGNORE", default_gitignore_file)
    gitignore_file = (
        gitignore_file
        if gitignore_file.endswith(".gitignore")
        else default_gitignore_file
    )
    with open(gitignore_file, "a+") as f:
        contents = f.read()
        for entry in gitignore_entries:
            if entry not in contents:
                f.write(entry)


def read_file(filename):
    with open(filename, "r") as f:
        contents = f.read()
    return contents


def write_file(contents, filename):
    if isinstance(contents, bytes):
        write_mode = "wb"
    else:
        write_mode = "w"
    with open(filename, write_mode) as f:
        f.write(contents)
