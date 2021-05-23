import os
import sys
import yaml
from typing import List

from conftest import TEST_DIR, LOQ_TEST_DIR
sys.path.append(os.path.join(os.path.dirname(TEST_DIR), "src"))

from loqet.encryption_suite import (
    encrypt_message, decrypt_message, validate_loq_file, read_loq_file,
    loq_encrypt_file, loq_decrypt_file, loq_file_search, load_loq_config
)   # noqa
from loqet.file_utils import read_file  # noqa


def test_generate_secret_key(loq_key: bytes, loq_test_dir: str) -> None:
    assert isinstance(loq_key, bytes)
    assert isinstance(loq_test_dir, str)


def test_message_encryption(loq_key: bytes) -> None:
    message = "It's dangerous to go alone, take this!"
    encrypted_message = encrypt_message(message=message, secret_key=loq_key)
    assert encrypted_message != message
    assert "dangerous" not in encrypted_message

    decrypted_message = decrypt_message(
        encrypted_message=encrypted_message,
        secret_key=loq_key
    )
    assert decrypted_message == message


def test_file_encryption(loq_key: bytes, sample_config_file: str) -> None:
    sample_config_file_contents = read_file(sample_config_file)
    loq_file = loq_encrypt_file(filename=sample_config_file, secret_key=loq_key)
    assert loq_file.endswith(".loq")
    assert validate_loq_file(loq_file)

    loq_file_raw_contents = read_file(loq_file)
    assert sample_config_file_contents != loq_file_raw_contents
    assert "inventory" not in loq_file_raw_contents

    decrypted_loq_file_contents = read_loq_file(
        loq_file=loq_file,
        secret_key=loq_key
    )
    assert decrypted_loq_file_contents == sample_config_file_contents

    open_file = loq_decrypt_file(loq_file=loq_file, secret_key=loq_key)
    assert open_file.endswith(".open")

    open_file_contents = read_file(open_file)
    assert open_file_contents == sample_config_file_contents


def test_load_loq_config(loq_key: bytes, sample_config_file: str) -> None:
    sample_config_file_contents = read_file(sample_config_file)
    loq_file = loq_encrypt_file(filename=sample_config_file, secret_key=loq_key)
    loaded_config = load_loq_config(loq_path=loq_file, secret_key=loq_key)
    assert loaded_config == yaml.safe_load(sample_config_file_contents)


def test_loq_search(loq_library: List[str]) -> None:
    loq_files = loq_file_search(LOQ_TEST_DIR)
    for loq_file_path in loq_library:
        assert loq_file_path in loq_files
        assert validate_loq_file(loq_file_path)
