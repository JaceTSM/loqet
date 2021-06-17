"""
Copyright (c) 2021, Timothy Murphy
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

---------------------------------------------------

Loqet Context Management

Tools for managing loqet contexts (project-specific secret stores)


# CLI Commands:
loqet context help      print help text
loqet context init      Create a loqet context
loqet context get       get name of active loqet context
loqet context list      list all loqet contexts
loqet context info      get config info about a context (default: active)
loqet context set       set active context
loqet context unset     unset active context


# Terms:
loq_config:     An encrypted yaml that stores secret configs.
                A loq_config's name is it's filename minus extension

loqet_context:  active project loqet to interact with. Consists of a list
                of loq files.

loqet:          A single namespace in a loqet context

"""

import os
import re
import yaml
from typing import Union
from loqet.secret_keys import write_secret_key
from loqet.loqet_configs import LOQET_CONTEXTS_FILE, INVALID_CONTEXT_NAMES
from loqet.exceptions import (
    LoqetInvalidConfigException,
    LoqetContextConflictException,
    LoqetInvalidContextException,
    LoqetNoSetContextException
)
from loqet.file_utils import update_gitignore


##################
# Context Config #
##################
# Associate one loqet secret store with a single project.
# Switch between contexts to switch between projects.


class ContextConfig(object):
    """
    Loqet saves a config defining multiple contexts. A context manages
    a single loqet secret store for a project.

    Context structure:
    context = {
        "loqet_dir": loqet_dir,
        "keyfile": keyfile,
    }
    """
    _config_defaults = {
        "active_context": None,
        "contexts": {},
    }

    def __init__(self, conf_file: str = LOQET_CONTEXTS_FILE) -> None:
        """Load config file into memory"""
        self._conf_file = conf_file
        if os.path.exists(self._conf_file):
            with open(self._conf_file, "r") as f:
                self._conf = yaml.safe_load(f)
            if self._conf is None:
                self._conf = {}
            elif not isinstance(self._conf, dict):
                raise LoqetInvalidConfigException(
                    f"{conf_file} is not a valid config file."
                )
        else:
            self._conf = {}

        # Ensure standard config keys are in conf
        for k, v in self._config_defaults.items():
            if not self._get_property(k):
                self._set_property(k, v)

    def _save_changes(self) -> None:
        """Write in-memory config to file"""
        with open(self._conf_file, "w") as f:
            yaml.safe_dump(self._conf, f)

    def _validate_context_name(self, name: str) -> None:
        if name in self._get_property("contexts"):
            raise LoqetContextConflictException(
                f"Context '{name}' exists already, taking no action"
            )
        if name.lower() in INVALID_CONTEXT_NAMES:
            raise LoqetInvalidContextException(
                f"Invalid context name '{name}'. "
                f"Context may not be any of: {INVALID_CONTEXT_NAMES}"
            )
        if not name:
            raise LoqetInvalidContextException(
                f"Invalid context name '{name}'. "
                f"Must contain at least one character"
            )
        if len(name) > 64:
            raise LoqetInvalidContextException(
                f"Invalid context name '{name}'. "
                f"Must be less than 64 characters."
            )
        if not re.match("^[^\\/?%*:|\"<>]+$", name):
            raise LoqetInvalidContextException(
                f"Invalid context name '{name}'. "
                f"Cannot contain invalid characters (\\/?%*:|\"<>)."
            )

    def _get_property(self, property_name: str) -> Union[str, dict, None]:
        """Extract single property value from in-memory config"""
        if property_name not in self._conf.keys():
            return None
        return self._conf[property_name]

    def _set_property(
            self,
            property_name: str,
            value: Union[str, dict, None]
    ) -> None:
        """Set in-memory config value"""
        self._conf[property_name] = value

    @property
    def active_context(self) -> str:
        """Get active loqet context"""
        return self._get_property("active_context")

    def set_active_context(self, context_name: str) -> bool:
        """Set active loqet context and save config to disk. returns success."""
        contexts = self.get_contexts()
        if context_name is None:
            self.unset_active_context()
        if context_name in contexts:
            self._set_property("active_context", context_name)
            self._save_changes()
            return True
        else:
            return False

    def unset_active_context(self) -> None:
        """Sets active context to None"""
        self._set_property("active_context", None)
        self._save_changes()

    def get_contexts(self) -> dict:
        """Get dict of all contexts from config"""
        return self._get_property("contexts") or {}

    def get_context(self, context_name: str) -> dict:
        """Get single context from config"""
        return self.get_contexts().get(context_name)

    def create_context(self, name: str, loqet_dir: str) -> None:
        """Create a loqet context and save its config to disk"""
        self._validate_context_name(name)
        keyfile_path = write_secret_key(context_name=name)
        self._conf["contexts"][name] = {
            "loqet_dir": os.path.abspath(loqet_dir),
            "keyfile": keyfile_path,
        }
        update_gitignore(loqet_dir)
        self._save_changes()

    def delete_context(self, name: str) -> None:
        """Remove context from config. Does not clean up key or context dir"""
        if self.active_context == name:
            self.unset_active_context()
        if name in self._conf.get("contexts"):
            del self._conf["contexts"][name]
            self._save_changes()


###############
# Context API #
###############

def create_loqet_context(context_name: str, loqet_dir: str) -> None:
    """
    Creates a named loqet secret store in the target directory,
    and uses the passed in key to encrypt those secrets. A key is
    automatically generated if none is provided. The secret key
    is stored in LOQET_CONTEXT_FILE (default: ~/.loqet/contexts.yaml)

    :param context_name:    Name of loqet context to create
    :param loqet_dir:       secret store directory to associate with loqet context
    :return:                n/a
    """
    context_config = ContextConfig()
    context_config.create_context(context_name, loqet_dir)


def get_active_context_name() -> str:
    """
    Get the name of the active loqet context

    :return:    name of active loqet context
    """
    context_config = ContextConfig()
    return context_config.active_context


def get_context_info(context_name: str = None) -> dict:
    """
    Returns keyfile, not the actual key content so it isn't written
    to console. Extract key in another method.

    :return: {
        "loqet_dir": _,
        "keyfile": _,
    }
    """
    context_config = ContextConfig()
    if not context_name:
        context_name = context_config.active_context
    context_info = context_config.get_context(context_name)
    return context_info


def set_loqet_context(name: str) -> bool:
    """Set active loqet context and save to config"""
    context_config = ContextConfig()
    success = context_config.set_active_context(name)
    return success


def unset_loqet_context() -> None:
    """Set active loqet context to None and save to config"""
    context_config = ContextConfig()
    context_config.unset_active_context()


def get_loqet_contexts() -> dict:
    """Get context configs"""
    context_config = ContextConfig()
    contexts = context_config.get_contexts()
    return contexts


##############
# Key Access #
##############

def get_context_key(context_info: dict) -> str:
    """Extract secret key from context config"""
    with open(context_info["keyfile"], "r") as f:
        key = f.read().strip()
    return key


def get_active_context_key() -> str:
    """Get secret key for active loqet context"""
    context_name = get_active_context_name()
    context_info = get_context_info(context_name)
    return get_context_key(context_info)


def get_context(context_name: str = None) -> (str, str):
    """get loqet dir and secret key for a given loqet context"""
    if not context_name:
        context_name = get_active_context_name()
        if not context_name:
            raise LoqetNoSetContextException(
                "No active context set and no context specified"
            )
    context_info = get_context_info(context_name)
    loqet_keyfile = context_info["keyfile"]
    loqet_dir = context_info["loqet_dir"]
    with open(loqet_keyfile, "rb") as f:
        secret_key = f.read()
    if isinstance(secret_key, bytes):
        secret_key = secret_key.decode()
    return loqet_dir, secret_key
