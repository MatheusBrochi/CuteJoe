import os

import pytest
from click.testing import CliRunner
from tempfile import TemporaryDirectory, NamedTemporaryFile
from unittest import mock

from cutejoe import cli
from cutejoe.helpers import Changelog, Config


@pytest.fixture(name="temp_folder")
def fixture_temp_folder():
    return TemporaryDirectory()


@pytest.fixture(name="temp_config_file")
def fixture_temp_config_file():
    temp_file = NamedTemporaryFile(mode="w")
    temp_file.writelines([
        "version: 1\n",
        "changelog:\n",
        "  default_title: 'Uncategorized'\n",
        "  folder: changelogs\n",
        "  start: master\n",
        "  end: HEAD\n",
    ])
    temp_file.seek(0)
    return temp_file


def test_config_file():
    runner = CliRunner()
    with runner.isolated_filesystem() as pwd:
        result = runner.invoke(cli, ["config-file"])

        with open(os.path.join(pwd, ".cutejoe.yml")) as file:
            assert file.readline() == "# CuteJoe 1.0 Configuration file\n"

    assert result.exit_code == 0
    assert "File created" in result.output


def test_config_file_with_folder(temp_folder):
    runner = CliRunner()

    result = runner.invoke(cli, ["config-file", f"--folder={temp_folder.name}"])

    assert result.exit_code == 0
    assert "File created" in result.output

    with open(os.path.join(temp_folder.name, ".cutejoe.yml")) as file:
        assert file.readline() == "# CuteJoe 1.0 Configuration file\n"


def test_config_file_already_exists():
    runner = CliRunner()

    with runner.isolated_filesystem():
        runner.invoke(cli, ["config-file"])
        result = runner.invoke(cli, ["config-file"])

    assert result.exit_code == 0
    assert "Config file already exists" in result.output
    # TODO assert file content


@mock.patch.object(Changelog, "content", return_value="Test content", new_callable=mock.PropertyMock)
@mock.patch.object(Changelog, "tag", return_value="v1.0.0", new_callable=mock.PropertyMock)
@mock.patch.object(Changelog, "branch", return_value="release/v1.0.0", new_callable=mock.PropertyMock)
def test_changelog(mock_content, mock_tag, mock_branch):
    runner = CliRunner()
    result = runner.invoke(cli, ["changelog"], input="y")

    assert result.exit_code == 0
    assert "Changelog:\nTest content" in result.output
    assert "Tag: \"v1.0.0\"" in result.output
    assert "Branch: \"release/v1.0.0\"" in result.output


def test_changelog_save(temp_folder):
    runner = CliRunner()
    file_name = os.path.join(temp_folder.name, "changelog.md")

    with mock.patch.object(Changelog, "file_path", return_value=file_name, new_callable=mock.PropertyMock):
        result = runner.invoke(cli, ["changelog", "--save"], input="y")

    assert result.exit_code == 0
    assert f"Changelog: \"{file_name}\"" in result.output


def test_changelog_with_start_end():
    runner = CliRunner()
    with mock.patch("cutejoe.helpers.changelog.get_unreleased_commits") as mock_commits:
        runner.invoke(cli, ["changelog", "--start=0123", "--end=0321"], input="y")

        mock_commits.assert_called_once_with("0123", "0321")


def test_changelog_with_config(temp_config_file):
    runner = CliRunner()

    with mock.patch.object(Config, "__init__") as mock_config:
        runner.invoke(cli, ["changelog", f"--config={temp_config_file.name}"])

        mock_config.assert_called_once_with(
            version=1,
            changelog={
                "default_title": "Uncategorized",
                "folder": "changelogs",
                "start": "master",
                "end": "HEAD",
            },
        )
