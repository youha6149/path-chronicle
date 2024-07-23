import importlib.util
from pathlib import Path


def get_package_root():
    """Get the root directory of the given package."""
    spec = importlib.util.find_spec(__package__)
    if spec is None or spec.origin is None:
        return None
    package_path = Path(spec.origin).parent

    return package_path
