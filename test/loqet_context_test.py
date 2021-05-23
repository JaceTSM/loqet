import os
import sys

from conftest import TEST_DIR
sys.path.append(os.path.join(os.path.dirname(TEST_DIR), "src"))

from loqet.loqet_contexts import (
    get_active_context_name, get_context_info,
    set_loqet_context, unset_loqet_context, get_loqet_contexts,
    get_context_key, get_active_context_key, get_context
)   # noqa


def test_create_loqet_context(loqet_context_name: str) -> None:
    contexts = get_loqet_contexts()
    assert loqet_context_name in contexts.keys()
    set_loqet_context(loqet_context_name)
    assert get_active_context_name() == loqet_context_name
    unset_loqet_context()
    assert get_active_context_name() is None


def test_loqet_key_actions(loqet_context_name: str) -> None:
    set_loqet_context(loqet_context_name)
    context_info = get_context_info(loqet_context_name)
    assert get_active_context_key() == get_context_key(context_info)
    loqet_dir, secret_key = get_context(loqet_context_name)
    assert secret_key == get_active_context_key()


def test_multiple_loqet_contexts(loqet_context_names: str) -> None:
    contexts = get_loqet_contexts()
    for context_name in loqet_context_names:
        assert context_name in contexts.keys()
        set_loqet_context(context_name)
        assert get_active_context_name() == context_name
        context_info = get_context_info(context_name)
        assert get_active_context_key() == get_context_key(context_info)
    unset_loqet_context()
    assert get_active_context_name() is None
