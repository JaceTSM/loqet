"""
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
import yaml
from loqet.secret_keys import write_secret_key
from loqet.loqet_configs import (
    LOQET_CONTEXTS_FILE, INVALID_CONTEXT_NAMES, LOQET_CONFIG_DIR
)
from loqet.exceptions import (
    LoqetInvalidConfigException,
    LoqetContextConflictException,
    LoqetInvalidContextException
)


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

    def __init__(self, conf_file=LOQET_CONTEXTS_FILE):
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

        for k, v in self._config_defaults.items():
            if k not in self._conf:
                self._conf[k] = v

    def _save_changes(self):
        with open(self._conf_file, "w") as f:
            yaml.safe_dump(self._conf, f)

    def _get_property(self, property_name):
        if property_name not in self._conf.keys():
            return None
        return self._conf[property_name]

    def _set_property(self, property_name, value):
        self._conf[property_name] = value

    @property
    def active_context(self):
        return self._get_property("active_context")

    def set_active_context(self, context_name):
        contexts = self.get_contexts()
        if context_name is None:
            self.unset_active_context()
        if context_name in contexts:
            self._set_property("active_context", context_name)
            self._save_changes()
            return True
        else:
            return False

    def unset_active_context(self):
        self._set_property("active_context", None)
        self._save_changes()

    def get_contexts(self):
        return self._get_property("contexts") or {}

    def get_context(self, context_name):
        return self.get_contexts().get(context_name)

    def create_context(self, name, loqet_dir):
        if name in self._conf["contexts"]:
            raise LoqetContextConflictException(
                f"Context '{name}' exists already, taking no action"
            )
        elif name.lower() in INVALID_CONTEXT_NAMES:
            raise LoqetInvalidContextException(
                f"Invalid context name '{name}'. "
                f"Context may not be any of: {INVALID_CONTEXT_NAMES}"
            )
        else:
            keyfile_path = write_secret_key(context_name=name)
            self._conf["contexts"][name] = {
                "loqet_dir": os.path.abspath(loqet_dir),
                "keyfile": keyfile_path,
            }
            self._save_changes()


###############
# Context API #
###############

def create_loqet_context(context_name, loqet_dir):
    """
    Creates a named loqet secret store in the target directory,
    and uses the passed in key to encrypt those secrets. A key is
    automatically generated if none is provided. The secret key
    is stored in LOQET_CONTEXT_FILE (default: ~/.loqet/contexts.yaml)
    """
    context_config = ContextConfig()
    context_config.create_context(context_name, loqet_dir)


def get_active_context_name():
    context_config = ContextConfig()
    return context_config.active_context


def get_context_info(context_name=None):
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


def set_loqet_context(name):
    context_config = ContextConfig()
    success = context_config.set_active_context(name)
    return success


def unset_loqet_context():
    context_config = ContextConfig()
    context_config.unset_active_context()


def get_loqet_contexts():
    context_config = ContextConfig()
    contexts = context_config.get_contexts()
    return contexts


##############
# Key Access #
##############

def get_context_key(context_info):
    with open(context_info["keyfile"], "r") as f:
        key = f.read().strip()
    return key


def get_active_context_key():
    context_name = get_active_context_name()
    context_info = get_context_info(context_name)
    return get_context_key(context_info)


def get_context(context_name=None):
    if not context_name:
        context_name = get_active_context_name()
    context_info = get_context_info(context_name)
    loqet_keyfile = context_info["keyfile"]
    loqet_dir = context_info["loqet_dir"]
    with open(loqet_keyfile, "rb") as f:
        secret_key = f.read()
    return loqet_dir, secret_key
