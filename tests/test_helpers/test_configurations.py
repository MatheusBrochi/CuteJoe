import pytest

from cutejoe.helpers.configurations import ChangelogConfigFactory, Config, ChangelogConfigV1
from cutejoe.helpers.configurations.base import BaseConfigFactory


class FakeConfig:

    def __init__(self, *args, **kwargs):
        self.variable = kwargs.get("variable")


def test_singleton_factory():
    first_factory = BaseConfigFactory()
    second_factory = BaseConfigFactory()
    assert first_factory is second_factory


def test_factory_register():
    BaseConfigFactory().register(2, FakeConfig)
    assert BaseConfigFactory()._configs[2] == FakeConfig


def test_factory_create():
    factory = BaseConfigFactory(2, FakeConfig)
    fake_config = factory.create(2, variable="test")
    assert isinstance(fake_config, FakeConfig)
    assert fake_config.variable == "test"


def test_factory_create_with_invalid_version():
    factory = BaseConfigFactory(2, FakeConfig)

    with pytest.raises(ValueError):
        factory.create("invalid", variable="test")


def test_changelog_factory_create_v1():
    changelog_config = ChangelogConfigFactory().create(1)
    assert isinstance(changelog_config, ChangelogConfigV1)


def test_config_changelog_by_version():
    config = Config(version=1, changelog={"folder": "test_folder"})
    changelog = config.changelog
    assert isinstance(changelog, ChangelogConfigV1)
    assert changelog.folder == "test_folder"


def test_config_get_default_file_path():
    assert Config.get_default_file_path().endswith("/.default_config.yml")


def test_changelog_v1():
    kwargs = {
        "folder": "test_folder",
        "start": "test_start",
        "end": "test_end",
        "default_title": "test_default",
        "kinds": {
            "add": {
                "labels": ["add", "added"],
                "title": "Added",
                "version": "minor",
            },
        },
    }
    changelog_config = ChangelogConfigFactory().create(1, **kwargs)
    assert changelog_config.folder == "test_folder"
    assert changelog_config.start == "test_start"
    assert changelog_config.end == "test_end"
    assert changelog_config.default_title == "test_default"
    assert changelog_config.kinds == {
        "add": {
            "labels": ["add", "added"],
            "title": "Added",
            "version": "minor",
        },
    }


def test_changelog_v1_with_default():
    changelog_config = ChangelogConfigFactory().create(1)
    assert changelog_config.folder == "changelogs"
    assert changelog_config.start == "master"
    assert changelog_config.end == "HEAD"
    assert changelog_config.default_title == "Uncategorized"
    assert changelog_config.kinds == {}


def test_changelog_v1_get_title():
    kwargs = {
        "default_title": "test_default",
        "kinds": {
            "add": {
                "labels": ["add", "added"],
                "title": "Added",
                "version": "minor",
            },
        },
    }
    changelog_config = ChangelogConfigFactory().create(1, **kwargs)
    assert changelog_config.get_title("add") == "Added"


def test_changelog_v1_get_title_with_invalid_kind():
    kwargs = {
        "default_title": "test_default",
        "kinds": {
            "add": {
                "labels": ["add", "added"],
                "title": "Added",
                "version": "minor",
            },
        },
    }
    changelog_config = ChangelogConfigFactory().create(1, **kwargs)
    assert changelog_config.get_title("added") == "test_default"


def test_changelog_v1_get_version():
    kwargs = {
        "default_title": "test_default",
        "kinds": {
            "add": {
                "labels": ["add", "added"],
                "title": "Added",
                "version": "minor",
            },
        },
    }
    changelog_config = ChangelogConfigFactory().create(1, **kwargs)
    assert changelog_config.get_version("add") == "minor"


def test_changelog_v1_get_version_with_invalid_kind():
    kwargs = {
        "default_title": "test_default",
        "kinds": {
            "add": {
                "labels": ["add", "added"],
                "title": "Added",
                "version": "minor",
            },
        },
    }
    changelog_config = ChangelogConfigFactory().create(1, **kwargs)
    assert changelog_config.get_version("added") is None


def test_changelog_v1_get_kind():
    kwargs = {
        "default_title": "test_default",
        "kinds": {
            "add": {
                "labels": ["add", "added"],
                "title": "Added",
                "version": "minor",
            },
        },
    }
    changelog_config = ChangelogConfigFactory().create(1, **kwargs)
    assert changelog_config.get_kind("added") == "add"


def test_changelog_v1_get_kind_with_invalid_label():
    kwargs = {
        "default_title": "test_default",
        "kinds": {
            "add": {
                "labels": ["add", "added"],
                "title": "Added",
                "version": "minor",
            },
        },
    }
    changelog_config = ChangelogConfigFactory().create(1, **kwargs)
    assert changelog_config.get_kind("invalid") is None
