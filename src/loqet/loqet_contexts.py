"""
Goals:

* Create a per-project secret-store
  - per-project secret key
  - manage loqet context (which loqet am I working on right now)
* manage secrets via cli and python api
* Manage configuration as dictionary in memory and yaml in file
  - most flexible for building on top of


Terms

loq_config:     An encrypted yaml that stores secret configs.
                A loq_config's name is it's filename minus extension

loqet_context:  active project loqet to interact with. Consists of a list
                of loq files.

loqet:          A single namespace in a loqet context

"""

import os
import yaml
from loqet.secret_keys import write_secret_key
from loqet.loqet_configs import LOQET_CONTEXTS_FILE, INVALID_CONTEXT_NAMES
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
            if not isinstance(self._conf, dict):
                raise LoqetInvalidConfigException(
                    f"{LOQET_CONTEXTS_FILE} is not a valid config file."
                )
        else:
            self._conf = {}

        for k, v in self._config_defaults.items():
            if k not in self._conf:
                self._conf[k] = v

    def _save_changes(self):
        with open(self._conf_file) as f:
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
        self._set_property("active_context", context_name)
        self._save_changes()

    def get_contexts(self):
        return self._get_property("contexts") or {}

    def get_context(self, context_name):
        return self.get_contexts().get(context_name)

    def create_context(self, name, loqet_dir, secret_key=None):
        if name in self._conf["contexts"]:
            raise LoqetContextConflictException(
                f"Context '{name}' exists already, taking no action"
            )
        elif name in INVALID_CONTEXT_NAMES:
            raise LoqetInvalidContextException(
                f"Invalid context name '{name}'. "
                f"Context may not be any of: {INVALID_CONTEXT_NAMES}"
            )
        else:
            keyfile = write_secret_key(secret_key)
            self._conf["contexts"][name] = {
                "loqet_dir": loqet_dir,
                "keyfile": keyfile,
            }
            self._save_changes()


###############
# Context API #
###############

# loqet init <context_name> <target_directory> [secret_key]
def create_loqet_context(context_name, loqet_dir, secret_key=None):
    """
    Creates a named loqet secret store in the target directory,
    and uses the passed in key to encrypt those secrets. A key is
    automatically generated if none is provided. The secret key
    is stored in LOQET_CONTEXT_FILE (default: ~/.loqet/contexts.yaml)
    """
    context_config = ContextConfig()
    context_config.create_context(context_name, loqet_dir, secret_key)


# loqet context get
def get_active_context_name():
    context_config = ContextConfig()
    return context_config.active_context


# loqet context info
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
    context = context_config.get_context(context_name)
    return context


# loqet context set
def set_loqet_context(name):
    context_config = ContextConfig()
    context_config.set_active_context(name)


# loqet context unset
def unset_loqet_context():
    set_loqet_context(None)


#######
# CLI #
#######
# TODO: move to cli script

# loqet context list
def list_loqet_contexts():
    context_config = ContextConfig()
    contexts = context_config.get_contexts()
    if not contexts:
        print(
            "No loqet contexts have been created. "
            "Create one with 'loqet init <context_name> <target_loqet_directory>'"
        )
        return
    longest_context = len(max(contexts.keys(), key=len))
    for context_name, context in contexts.items():
        print(f"{context_name.ljust(longest_context + 1)}: {context['loqet_dir']}")


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
    loqet_dir = context_info["loquet_dir"]
    with open(loqet_keyfile, "rb") as f:
        secret_key = f.read()
    return loqet_dir, secret_key
