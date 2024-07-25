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
