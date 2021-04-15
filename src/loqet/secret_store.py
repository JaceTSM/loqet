import os

from src.loqet.loqet_contexts import get_context_info
from src.loqet.loqet_configs import LOQET_CONFIG_DIR, LOQ_EXTENSION
from src.loqet.encryption_suite import unloq_file, loq_file


####################
# Loqet Management #
####################

# def list_loqet_dir(loqet_name):
#     context = get_context_info(loqet_name)
#     loqet_dir = context["loquet_dir"]
#     return os.listdir(loqet_dir)


def open_loqet(loqet_name, safe=True):
    """
    Decrypt all loq_config files in named loqet

    Will create/update .gitignore and make .bak files
    if safe is True (default:true)
    """
    context = get_context_info(loqet_name)
    loqet_keyfile = context["keyfile"]
    loqet_dir = context["loquet_dir"]
    with open(loqet_keyfile, "rb") as f:
        secret_key = f.read()
    loq_files = [f for f in os.listdir(loqet_dir) if f.endswith(LOQ_EXTENSION)]
    for loq_file in loq_files:
        unloq_file(loq_file, secret_key, safe=safe)


def close_loqet(loqet_name, safe=True):
    """
    Encrypts all non-loq_config files in named loqet
    """
    context = get_context_info(loqet_name)
    loqet_keyfile = context["keyfile"]
    loqet_dir = context["loquet_dir"]
    with open(loqet_keyfile, "rb") as f:
        secret_key = f.read()
    open_files = [f for f in os.listdir(loqet_dir) if not f.endswith(LOQ_EXTENSION)]
    for open_file in open_files:
        loq_file(open_file, secret_key, safe=safe)


def load_loqet(loqet_name, namespace):
    valid_extensions = [".yaml", ".yaml.open", ".yaml.loq"]
    context = get_context_info(loqet_name)
    loqet_dir = context["loquet_dir"]
    matches = [
        f for f in os.listdir(loqet_dir)
        if f.split(".")[0] == namespace
    ]
    # CURRENT PROGRESS:
    #   Should we drop the ".open" extension idea? just swap between
    #   yaml and loq files? Adding the `loq` extension preserves file
    #   typing, so something is either a .loq or not.
    #
    #   Currently the thought is that having all three filetypes at once
    #   would be really confusing, and make precedence weird.


#################
# Secret Access #
#################
# Creating/Retrieving/Updating/Deleting secrets in a loqet

def load_loq_config(loq_config):
    """Decrypts a vaulted config file and loads it as yaml"""
    loq_contents = read_loq_file(loq_config)
    config = yaml.safe_load(loq_contents)
    return config


def quick_load(vault_name):
    """
    quick_load('my_secrets') will load the contents of ${loqet_dir}/my_secrets.yaml.loq
    """
    vault_file = f"{vault_name}.yaml.loq"
    vault_config = os.path.join(VAULT_DIR, vault_file)
    return load_loq_config(vault_config)
