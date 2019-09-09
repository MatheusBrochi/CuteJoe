from tempfile import NamedTemporaryFile

import pytest
import yaml
from unittest import mock

from cutejoe.helpers.utils import (
    command_process, get_project_url, get_unreleased_commits, get_last_tag,
    read_text_file, read_yml_file, save_text_file,
)


@pytest.fixture(name="temp_file")
def fixture_temp_file():
    temp_file = NamedTemporaryFile("w+")
    return temp_file


def test_command_process():
    assert command_process("echo 'Test'") == "'Test'\n"


def test_get_project_url():
    assert get_project_url() == "https://github.com/MatheusBrochi/CuteJoe"


@mock.patch("cutejoe.helpers.utils.command_process", return_value="https://github.com/MatheusBrochi/CuteJoe")
def test_get_project_url_with_ssh(mock_command):
    assert get_project_url() == "https://github.com/MatheusBrochi/CuteJoe"


@mock.patch("cutejoe.helpers.utils.command_process", return_value="git@github.com:MatheusBrochi/CuteJoe.git")
def test_get_project_url_with_https(mock_command):
    assert get_project_url() == "https://github.com/MatheusBrochi/CuteJoe"


def test_get_unreleased_commits():
    commits = get_unreleased_commits("7b30db2", "7a28a58")
    assert commits.replace("\r", "").replace("\n", "") == (
        "'add:initial setup, readmeadd:changelog and config commands'"
    )


def test_get_last_tag():
    assert get_last_tag() == "v0.0.0"


@mock.patch("cutejoe.helpers.utils.command_process", side_effect=Exception)
def test_get_last_tag_without_tag(mock_command):
    assert get_last_tag() == "v0.0.0"


@mock.patch("cutejoe.helpers.utils.command_process", return_value="v0.1.0-extra")
def test_get_last_tag_with_tag(mock_command):
    assert get_last_tag() == "v0.1.0"


def test_read_text_file(temp_file):
    temp_file.writelines(["first_line\n", "last_line\n"])
    temp_file.seek(0)

    content = read_text_file(temp_file.name)

    assert content == [
        "first_line\n",
        "last_line\n",
    ]


def test_read_yml_file(temp_file):
    temp_file.writelines([
        "# test_header\n",
        "key:\n",
        "  - first_value\n",
        "  - second_value\n",
    ])
    temp_file.seek(0)
    content = read_yml_file(temp_file.name)

    assert content == {
        "key": ["first_value", "second_value"],
    }


def test_read_invalid_yml_file(temp_file):
    temp_file.writelines([
        "# test_header\n",
        "teste:\n",
        "    - a\n",
        "    c\n",
    ])
    temp_file.seek(0)

    with pytest.raises(yaml.YAMLError):
        read_yml_file(temp_file.name)


def test_save_text_file(temp_file):
    content = ["first_line\n", "last_line\n"]

    assert save_text_file(str(temp_file.name), content) == temp_file.name

    temp_file.seek(0)
    lines = temp_file.readlines()

    assert lines == ["first_line\n", "last_line\n"]
    temp_file.close()
