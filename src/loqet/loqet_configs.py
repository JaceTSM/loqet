"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""

import os


LOQ_EXTENSION = ".loq"
OPEN_EXTENSION = ".open"

USER_HOME = os.path.expanduser("~")

# Editor to use with interactive encrypted file editor
EDITOR = os.environ.get("EDITOR", "vim")

# When true, make backups of .loq files on write and edit
SAFE_MODE = os.environ.get("LOQET_SAFE_MODE", False)

# Don't make contexts with these names pls
INVALID_CONTEXT_NAMES = [
    "",
    "none",
    "loqet",
]

# Where loqet configs are stored, such as your loqet secret key
DEFAULT_LOQET_CONFIG_DIR = os.path.join(USER_HOME, ".loqet")
LOQET_CONFIG_DIR = os.environ.get("LOQET_CONFIG_DIR", DEFAULT_LOQET_CONFIG_DIR)

# Secret key to encrypt/decrypt files not associated with a loqet context
DEFAULT_LOQ_KEY_FILE = os.path.join(LOQET_CONFIG_DIR, "loq.key")
LOQ_KEY_FILE = os.environ.get("LOQ_KEY_FILE", DEFAULT_LOQ_KEY_FILE)

# Where loqet context info is kept
DEFAULT_LOQET_CONTEXTS_FILE = os.path.join(LOQET_CONFIG_DIR, "contexts.yaml")
LOQET_CONTEXTS_FILE = os.environ.get("LOQET_CONFIG_FILE", DEFAULT_LOQET_CONTEXTS_FILE)
