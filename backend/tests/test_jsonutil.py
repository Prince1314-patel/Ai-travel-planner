import pytest

from jsonutil import extract_json_object


def test_extracts_json_from_plain_object():
    assert extract_json_object('{"a": 1}') == {"a": 1}


def test_extracts_json_embedded_in_prose():
    text = 'Sure, here you go:\n{"a": 1, "b": [1, 2]}\nHope that helps!'
    assert extract_json_object(text) == {"a": 1, "b": [1, 2]}


def test_raises_when_no_braces_present():
    with pytest.raises(ValueError):
        extract_json_object("no json here")


def test_raises_when_braces_contain_invalid_json():
    with pytest.raises(ValueError):
        extract_json_object("{not valid json}")
