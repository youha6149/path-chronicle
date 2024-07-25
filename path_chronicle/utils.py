import importlib.util
from pathlib import Path


def get_package_root() -> Path | None:
    """
    Returns the root directory of the current package.

    Returns:
        Path | None: The root directory of the package,
                     or None if the package is not found.
    """

    spec = importlib.util.find_spec(__package__)
    if spec is None or spec.origin is None:
        return None
    package_path = Path(spec.origin).parent

    return package_path


def find_project_root(current_path: Path, project_name: str) -> Path:
    """
    Finds the project root directory given the current path and project name.

    Args:
        current_path (Path): The current path from which to start searching.
        project_name (str): The name of the project root directory.

    Returns:
        Path: The path to the project root directory.

    Raises:
        FileNotFoundError:
        If the project root directory with the given name is not found.
    """
    for parent in current_path.parents:
        if parent.name == project_name:
            return parent
    raise FileNotFoundError(f"Project root with name '{project_name}' not found.")
