import os
import pytest
import shutil
import sys
import yaml
from typing import List

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
LOQ_TEST_DIR = os.path.join(TEST_DIR, "loq_test")
LOQET_TEST_DIR = os.path.join(TEST_DIR, "loqet_test")
sys.path.append(os.path.join(os.path.dirname(TEST_DIR), "src"))

from loqet.loqet_contexts import (
    create_loqet_context, get_context_info, get_loqet_contexts,
    set_loqet_context, ContextConfig
)   # noqa
from loqet.secret_store import (
    create_loqet, encrypt_loqet, list_loqet_filenames
)   # noqa
from loqet.secret_keys import generate_secret_key   # noqa
from loqet.encryption_suite import write_loq_file   # noqa
from loqet.file_utils import write_file     # noqa


#############################
# Encryption Suite Fixtures #
#############################

SAMPLE_CONFIG = {
    "sword": "master sword",
    "shield": "mirror shield",
    "bottles": {
        "slot_1": "fairy",
        "slot_2": "poe",
    },
}


@pytest.fixture(scope="session")
def loq_key() -> bytes:
    return generate_secret_key()


@pytest.fixture(scope="module")
def loq_test_dir() -> str:
    os.mkdir(LOQ_TEST_DIR)
    yield LOQ_TEST_DIR
    shutil.rmtree(LOQ_TEST_DIR)


@pytest.fixture(scope="function")
def sample_config_file(loq_test_dir: str) -> str:
    config_file = os.path.join(loq_test_dir, "sample_config.yaml")
    config_yaml_data = yaml.dump(SAMPLE_CONFIG)
    write_file(config_yaml_data, config_file)
    yield config_file
    if os.path.exists(config_file):
        os.remove(config_file)


@pytest.fixture(scope="function")
def loq_library(loq_test_dir: str, loq_key: bytes) -> List[str]:
    confs = [SAMPLE_CONFIG.copy(), SAMPLE_CONFIG.copy(), SAMPLE_CONFIG.copy()]
    conf_paths = []
    confs[1]["sword"] = "biggoron sword"
    confs[2]["shield"] = "hylian shield"
    for i, conf in enumerate(confs):
        conf_path = os.path.join(LOQ_TEST_DIR, f"conf_{i}.yaml.loq")
        write_loq_file(
            contents=yaml.dump(conf),
            filename=conf_path,
            secret_key=loq_key
        )
        conf_paths.append(conf_path)
    yield conf_paths
    for conf_path in conf_paths:
        if os.path.exists(conf_path):
            os.remove(conf_path)


#########################
# Secret Store Fixtures #
#########################

def create_test_loqet_context(context_name: str) -> str:
    print(f"Creating {context_name} context")
    loqet_dir = os.path.join(LOQET_TEST_DIR, context_name)
    os.mkdir(loqet_dir)
    create_loqet_context(
        context_name=context_name,
        loqet_dir=loqet_dir
    )
    return loqet_dir


def cleanup_test_loqet_context(context_name: str) -> None:
    print(f"Cleaning up {context_name} context")
    context_info = get_context_info(context_name=context_name)
    loqet_dir = context_info["loqet_dir"]
    loqet_key = context_info["keyfile"]
    ctx = ContextConfig()
    ctx.delete_context(name=context_name)
    shutil.rmtree(loqet_dir)
    if os.path.exists(loqet_key):
        os.remove(loqet_key)


def context_name_panic(name: str) -> None:
    """If any of the test context names exist, bail."""
    assert name not in get_loqet_contexts().keys(), \
        f"Context '{name}' already exists."


@pytest.fixture(scope="module")
def loqet_test_dir() -> str:
    os.mkdir(LOQET_TEST_DIR)
    yield LOQET_TEST_DIR
    shutil.rmtree(LOQET_TEST_DIR)


@pytest.fixture(scope="function")
def loqet_context_name(loqet_test_dir: str) -> None:
    context_name = "link"
    context_name_panic(context_name)
    _ = create_test_loqet_context(context_name=context_name)
    yield context_name
    cleanup_test_loqet_context(context_name=context_name)


@pytest.fixture(scope="function")
def loqet_context_names(loqet_test_dir: str, loqet_context_name: str) -> List[str]:
    additional_context_names = ["zelda", "navi"]
    for context_name in additional_context_names:
        context_name_panic(context_name)
        _ = create_test_loqet_context(context_name=context_name)
    context_names = [loqet_context_name] + additional_context_names
    yield context_names
    for context_name in additional_context_names:
        cleanup_test_loqet_context(context_name=context_name)


@pytest.fixture(scope="function")
def loqet_name(loqet_context_name: str) -> str:
    sample_loqet_name = "inventory"
    set_loqet_context(name=loqet_context_name)
    create_loqet(sample_loqet_name)
    yield sample_loqet_name
    loqet_file_names = list_loqet_filenames(
        loqet_name=loqet_name,
        context_name=loqet_context_name
    )
    for loqet_file_name in loqet_file_names:
        if os.path.exists(loqet_file_name):
            os.remove(loqet_file_name)


@pytest.fixture(scope="function")
def sample_loqet_open_file(loqet_name: str, loqet_context_name: str) -> str:
    set_loqet_context(name=loqet_context_name)
    config_file = os.path.join(
        LOQET_TEST_DIR,
        loqet_context_name,
        f"{loqet_name}.yaml.open"
    )
    config_yaml_data = yaml.dump(SAMPLE_CONFIG)
    write_file(config_yaml_data, config_file)
    yield config_file
    if os.path.exists(config_file):
        os.remove(config_file)


@pytest.fixture(scope="function")
def sample_loqet_loq_file(
        loqet_context_name: str,
        loqet_name: str,
        sample_loqet_open_file: str     # noqa
) -> str:
    loq_file_name = os.path.join(
        LOQET_TEST_DIR,
        loqet_context_name,
        f"{loqet_name}.yaml.loq"
    )
    encrypt_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    yield loq_file_name
    if os.path.exists(loq_file_name):
        os.remove(loq_file_name)
