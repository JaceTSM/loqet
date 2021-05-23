import os
import sys
import yaml

from conftest import TEST_DIR, LOQET_TEST_DIR, SAMPLE_CONFIG
sys.path.append(os.path.join(os.path.dirname(TEST_DIR), "src"))

from loqet.encryption_suite import validate_loq_file    # noqa
from loqet.secret_store import (
    list_loqet_filenames, get_precedent_loqet_filename, load_loqet,
    list_loqets, list_loqet_dir, encrypt_loqet, decrypt_loqet,
    close_loqets, open_loqets, loqet_get, create_loqet
)   # noqa
from loqet.file_utils import read_file, write_file  # noqa


def test_loqet_create(loqet_name: str, loqet_context_name: str) -> None:
    assert loqet_name in list_loqets(context_name=loqet_context_name)


def test_list_loqet_files(loqet_name: str, sample_loqet_open_file: str) -> None:
    open_file_basename = os.path.basename(sample_loqet_open_file)
    assert open_file_basename in list_loqet_dir()
    assert open_file_basename in list_loqet_filenames(loqet_name=loqet_name)


def test_loqet_encryption(
        loqet_context_name: str,
        loqet_name: str,
        sample_loqet_open_file: str
) -> None:
    original_open_contents = read_file(sample_loqet_open_file)
    loq_file_name = os.path.join(
        LOQET_TEST_DIR,
        loqet_context_name,
        f"{loqet_name}.yaml.loq"
    )
    encrypt_loqet(loqet_name=loqet_name, context_name=loqet_context_name)

    assert os.path.exists(loq_file_name)
    assert validate_loq_file(loq_file_name)
    loq_raw_contents = read_file(loq_file_name)
    assert loq_raw_contents != original_open_contents
    os.remove(sample_loqet_open_file)
    decrypt_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    assert read_file(sample_loqet_open_file) == original_open_contents


def test_loqet_precedence(
        loqet_context_name: str,
        loqet_name: str,
        sample_loqet_open_file: str
) -> None:
    loq_file_name = os.path.join(LOQET_TEST_DIR, f"{loqet_name}.yaml.loq")
    precedent_file_name = get_precedent_loqet_filename(
        loqet_name=loqet_name,
        context_name=loqet_context_name
    )
    assert sample_loqet_open_file.endswith(precedent_file_name)

    encrypt_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    precedent_file_name = get_precedent_loqet_filename(
        loqet_name=loqet_name,
        context_name=loqet_context_name
    )
    assert sample_loqet_open_file.endswith(precedent_file_name)

    os.remove(sample_loqet_open_file)
    precedent_file_name = get_precedent_loqet_filename(
        loqet_name=loqet_name,
        context_name=loqet_context_name
    )
    assert loq_file_name.endswith(precedent_file_name)

    decrypt_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    precedent_file_name = get_precedent_loqet_filename(
        loqet_name=loqet_name,
        context_name=loqet_context_name
    )
    assert sample_loqet_open_file.endswith(precedent_file_name)


def test_load_loqet(
        loqet_context_name: str,
        loqet_name: str,
        sample_loqet_open_file: str,
        sample_loqet_loq_file: str
) -> None:
    os.remove(sample_loqet_open_file)
    contents = load_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    assert contents == SAMPLE_CONFIG

    decrypt_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    os.remove(sample_loqet_loq_file)
    contents = load_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    assert contents == SAMPLE_CONFIG

    new_config = SAMPLE_CONFIG.copy()
    new_sword = "biggoron sword"
    new_config["sword"] = new_sword
    write_file(yaml.dump(new_config), sample_loqet_open_file)
    encrypt_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    os.remove(sample_loqet_open_file)
    contents = load_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
    assert contents == new_config

    loaded_sword = loqet_get(
        loqet_namespace_path=f"{loqet_name}.sword",
        context_name=loqet_context_name
    )
    assert loaded_sword == new_sword

    bad_path_value = loqet_get(
        loqet_namespace_path=f"{loqet_name}.sword.insignia",
        context_name=loqet_context_name
    )
    assert bad_path_value == {}


def test_open_close_loqet(loqet_context_name: str) -> None:
    loqet_names = ["inventory", "songs", "bosses"]
    open_file_names = []
    loq_file_names = []
    for loqet_name in loqet_names:
        create_loqet(loqet_name=loqet_name, context_name=loqet_context_name)
        open_file_names.append(f"{loqet_name}.yaml.open")
        loq_file_names.append(f"{loqet_name}.yaml.loq")
    close_loqets(context_name=loqet_context_name)
    for loq_file_name in loq_file_names:
        assert loq_file_name in list_loqet_dir(context_name=loqet_context_name)
    for open_file_name in open_file_names:
        assert open_file_name in list_loqet_dir(context_name=loqet_context_name)
        open_path = os.path.join(
            LOQET_TEST_DIR, loqet_context_name, open_file_name
        )
        os.remove(open_path)
    open_loqets(context_name=loqet_context_name)
    for open_file_name in open_file_names:
        assert open_file_name in list_loqet_dir(context_name=loqet_context_name)
