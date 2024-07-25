import json
from pathlib import Path

from path_chronicle.config import Config

ABS_PATH = Path().cwd()


def test_load_config_nonexistent_file(setup_env):
    """
    Test loading configuration when the config file does not exist.

    Args:
        setup_env (Path): The temporary environment directory.

    Assert:
        The configuration should be empty.
    """
    config = Config(setup_env)
    assert (
        config.config == {}
    ), "Config should be empty when config file does not exist."


def test_load_config_existing_file(setup_config_file, setup_env):
    """
    Test loading configuration from an existing config file.

    Args:
        setup_config_file (Path): Path to the setup config file.
        setuo_env (Path): The temporary environment directory.

    Assert:
        The configuration should match the data in the config file.
    """
    config_data = {"project_root": "/path/to/project"}
    with open(setup_config_file, "w") as file:
        json.dump(config_data, file)

    config = Config(setup_env)
    assert (
        config.config == config_data
    ), "Config should match the data in the config file."


def test_get_config_value(setup_config_file, setup_env):
    """
    Test getting a value from the configuration.

    Args:
        setup_config_file (Path): Path to the setup config file.
        setup_env (Path): The temporary environment directory.

    Assert:
        The correct value should be returned.
    """
    config_data = {"project_root": "/path/to/project"}
    with open(setup_config_file, "w") as file:
        json.dump(config_data, file)

    config = Config(setup_env)
    assert (
        config.get("project_root") == "/path/to/project"
    ), "Should return the correct value for project_root."


def test_set_config_value(setup_config_file, setup_env):
    """
    Test setting a value in the configuration.

    Args:
        setup_config_file (Path): Path to the setup config file.
        setup_env (Path): The temporary environment directory.

    Assert:
        The value should be set in the configuration.
        The config file should contain the new value.
    """
    config = Config(setup_env)

    config.set("project_root", "/new/path/to/project")

    assert (
        config.get("project_root") == "/new/path/to/project"
    ), "Should return the newly set value for project_root."

    with open(setup_config_file, "r") as file:
        config_data = json.load(file)
        assert (
            config_data["project_root"] == "/new/path/to/project"
        ), "Config file should contain the newly set value."


def test_set_project_root_from_relative(setup_env):
    """
    Test setting the project root directory to an absolute path.

    Args:
        setup_env (Path): The temporary environment directory.

    Assert:
        The project root should be set to the absolute path.
    """
    config = Config(package_root=setup_env)
    config.set_project_root("project_root")

    actual_project_root = Path(config.get("project_root"))
    expected_project_root = Path("project_root").resolve()
    assert (
        actual_project_root == expected_project_root
    ), "Should return the newly set value for project_root. "
    f"Expected: {expected_project_root}, but got: {actual_project_root}"

    config_file = config.get_config_file()
    with open(config_file, "r") as file:
        config_data = json.load(file)
        assert config_data["project_root"] == str(
            expected_project_root
        ), "Config file should contain the newly set value."


def test_set_project_root_from_absolute(setup_env):
    """
    Test setting the project root directory to an absolute path.

    Args:
        setup_env (Path): The temporary environment directory.

    Assert:
        The project root should be set to the absolute path
    """
    config = Config(package_root=setup_env)
    config.set_project_root(setup_env.resolve())

    actual_project_root = Path(config.get("project_root"))
    expected_project_root = setup_env.resolve()
    assert (
        actual_project_root == expected_project_root
    ), "Should return the newly set value for project_root. "
    f"Expected: {expected_project_root}, but got: {actual_project_root}"

    config_file = config.get_config_file()
    with open(config_file, "r") as file:
        config_data = json.load(file)
        assert config_data["project_root"] == str(
            expected_project_root
        ), "Config file should contain the newly set value."
