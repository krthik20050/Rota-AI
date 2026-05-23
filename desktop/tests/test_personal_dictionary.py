"""Tests for PersonalDictionary in ai.personal_dictionary."""
import os
import json
import pytest
from ai.personal_dictionary import PersonalDictionary


@pytest.fixture
def dict_path(tmp_path):
    return str(tmp_path / "personal_dict.json")


def test_empty_on_first_use(dict_path):
    pd = PersonalDictionary(dict_path=dict_path)
    assert pd.get_terms() == []


def test_learn_technical_terms(dict_path):
    pd = PersonalDictionary(dict_path=dict_path)
    pd.learn_from_text("I use PyQt6 every day.")
    terms = pd.get_terms()
    assert "PyQt6" in terms


def test_persists_across_instances(dict_path):
    pd1 = PersonalDictionary(dict_path=dict_path)
    pd1.learn_from_text("I use PyQt6 every day.")
    pd1._save()

    pd2 = PersonalDictionary(dict_path=dict_path)
    assert pd2.get_terms() != []


def test_get_terms_returns_list(dict_path):
    pd = PersonalDictionary(dict_path=dict_path)
    assert isinstance(pd.get_terms(), list)


def test_corrupt_file_recovers(dict_path):
    with open(dict_path, "w") as f:
        f.write("not valid json {{{")
    pd = PersonalDictionary(dict_path=dict_path)
    assert pd.get_terms() == []


def test_save_creates_file(dict_path):
    pd = PersonalDictionary(dict_path=dict_path)
    pd.learn_from_text("TensorFlow is a framework.")
    pd._save()
    assert os.path.exists(dict_path)
    with open(dict_path) as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_all_terms_returns_dict(dict_path):
    pd = PersonalDictionary(dict_path=dict_path)
    pd.learn_from_text("PyQt6 is a library.")
    result = pd.all_terms()
    assert isinstance(result, dict)


def test_add_and_remove_term(dict_path):
    pd = PersonalDictionary(dict_path=dict_path)
    pd.add_term("CustomWord")
    assert "CustomWord" in pd.get_terms()
    pd.remove_term("CustomWord")
    assert "CustomWord" not in pd.get_terms()
