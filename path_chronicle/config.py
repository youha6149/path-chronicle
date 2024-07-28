import json
from pathlib import Path

from path_chronicle.utils import get_package_root


class Config:
    """
    A class representing the configuration settings for the application.
    """

    def __init__(self, package_root: Path | None = None):
        self.package_root = get_package_root() if package_root is None else package_root
        self.config = self.load_config()

    def load_config(self) -> dict:
        """
        Loads the configuration from the config file.

        Returns:
            dict: The loaded configuration settings.
        """
        config = {}
        config_file = self.get_config_file()
        if config_file.exists():
            with open(config_file, "r") as file:
                config = json.load(file)
        return config

    def get_config_file(self) -> Path:
        """
        Gets the path to the config file.

        Returns:
            Path: The path to the config file.
        """
        if self.package_root is None:
            raise ValueError("Package root directory not set.")

        config_dir = self.package_root / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"

    def get(self, key: str) -> str | int | float | bool | None:
        """
        Gets the value associated with the given key from the configuration.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            Any: The value associated with the key, or None if the key is not found.
        """
        return self.config.get(key, None)

    def set(self, key: str, value: str | int | float | bool):
        """
        Sets the value for the given key in the configuration.

        Args:
            key (str): The key to set the value for.
            value (Any): The value to set.
        """
        self.config[key] = value
        with open(self.get_config_file(), "w") as file:
            json.dump(self.config, file)

    def set_project_root(self, project_root: str):
        """
        Sets the project root directory in the configuration.

        Args:
            project_root (str): The project root directory path.

        Note:
            The project root directory path will always be stored as an absolute path.
        """
        project_root_path = Path(project_root)

        # If the provided path is not absolute, resolve it to an absolute path
        if not project_root_path.is_absolute():
            project_root_path = project_root_path.resolve()

        # Store the project root as an absolute path in the configuration
        self.set("project_root", str(project_root_path))
