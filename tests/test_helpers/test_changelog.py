import datetime

import pytest
from unittest import mock

from cutejoe.helpers import Changelog
from cutejoe.helpers.configurations import ChangelogConfigV1


@pytest.fixture(name="changelog")
def fixture_changelog():
    config = ChangelogConfigV1(kinds={
        "break": {"labels": ["break"], "title": "Breaking", "version": "major"},
        "add": {"labels": ["added", "adding"], "title": "Added", "version": "minor"},
        "fix": {"labels": ["fixed"], "title": "Fixed", "version": "patch"},
    })
    return Changelog(config=config)


@mock.patch.object(Changelog, "tag", return_value="v1.0.0", new_callable=mock.PropertyMock)
def test_branch(mock_tag, changelog):
    assert changelog.branch == "release/v1.0.0"


@mock.patch.object(Changelog, "_get_grouped_commits", return_value={"add": ["test1"], "break": ["test2"]})
@mock.patch("cutejoe.helpers.changelog.get_project_url", return_value="https://test.com")
@mock.patch("cutejoe.helpers.changelog.get_last_tag", return_value="v0.1.0")
def test_content(mock_commits, mock_url, mock_tag, changelog):
    expected = [
        "### Added\n",
        "- test1\n",
        "\n",
        "### Breaking\n",
        "- test2\n",
        "\n",
        "[v1.0.0]: https://test.com/compare/v0.1.0..v1.0.0\n",
    ]
    assert changelog.content == expected


@mock.patch.object(Changelog, "_get_grouped_commits", return_value={})
@mock.patch("cutejoe.helpers.changelog.get_project_url", return_value="https://test.com")
@mock.patch("cutejoe.helpers.changelog.get_last_tag", return_value="v0.1.0")
def test_content_without_commits(mock_commits, mock_url, mock_tag, changelog):
    expected = [
        "[v0.1.1]: https://test.com/compare/v0.1.0..v0.1.1\n",
    ]
    assert changelog.content == expected


@mock.patch.object(Changelog, "_get_grouped_commits", return_value={"add": ["test1"], "break": ["test2"]})
@mock.patch("cutejoe.helpers.changelog.get_project_url", return_value="")
@mock.patch("cutejoe.helpers.changelog.get_last_tag", return_value="v0.1.0")
def test_content_without_url(mock_commits, mock_url, mock_tag, changelog):
    expected = [
        "### Added\n",
        "- test1\n",
        "\n",
        "### Breaking\n",
        "- test2\n",
        "\n",
    ]
    assert changelog.content == expected


@mock.patch.object(Changelog, "tag", return_value="v1.0.0", new_callable=mock.PropertyMock)
def test_file_path(mock_tag, changelog):
    with mock.patch("cutejoe.helpers.changelog.date", mock.Mock(wraps=datetime.date)) as mock_date:
        mock_date.today = lambda: datetime.date(2019, 8, 25)
        assert changelog.file_path == "changelogs/[v1.0.0] - 2019-08-25.md"


@mock.patch("cutejoe.helpers.changelog.get_last_tag", return_value="v0.1.1")
@mock.patch.object(Changelog, "_get_tag_increment_position", return_value=0)
def test_tag_with_major(mock_tag, mock_increment, changelog):
    assert changelog.tag == "v1.0.0"


@mock.patch("cutejoe.helpers.changelog.get_last_tag", return_value="v0.1.1")
@mock.patch.object(Changelog, "_get_tag_increment_position", return_value=1)
def test_tag_with_minor(mock_tag, mock_increment, changelog):
    assert changelog.tag == "v0.2.0"


@mock.patch("cutejoe.helpers.changelog.get_last_tag", return_value="v0.1.1")
@mock.patch.object(Changelog, "_get_tag_increment_position", return_value=2)
def test_tag_with_patch(mock_tag, mock_increment, changelog):
    assert changelog.tag == "v0.1.2"


@mock.patch.object(Changelog, "_get_kinds", return_value={"add", "break"})
def test_get_tag_increment_position_with_major(mock_kind, changelog):
    assert changelog._get_tag_increment_position() == 0


@mock.patch.object(Changelog, "_get_kinds", return_value={"add", "fix"})
def test_get_tag_increment_position_with_minor(mock_kind, changelog):
    assert changelog._get_tag_increment_position() == 1


@mock.patch.object(Changelog, "_get_kinds", return_value={"fix"})
def test_get_tag_increment_position_with_patch(mock_kind, changelog):
    assert changelog._get_tag_increment_position() == 2


@mock.patch.object(Changelog, "_get_grouped_commits", return_value={"add": ["test1", "test3"], "break": ["test2"]})
def test_get_kinds(mock_commits, changelog):
    assert changelog._get_kinds() == {"add", "break"}


@mock.patch("cutejoe.helpers.changelog.get_unreleased_commits", return_value="added:test1\nbreak:test2\nadding:test 3")
def test_get_grouped_commits(mock_commits, changelog):
    expected = {
        "add": ["test1", "test 3"],
        "break": ["test2"],
    }
    assert changelog._get_grouped_commits() == expected


@mock.patch("cutejoe.helpers.changelog.get_unreleased_commits", return_value="added:test1\nadding:test2 \nbreak: ")
def test_get_grouped_commits_with_empty(mock_commits, changelog):
    expected = {
        "add": ["test1", "test2"],
    }
    assert changelog._get_grouped_commits() == expected
