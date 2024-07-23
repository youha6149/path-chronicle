import csv
from pathlib import Path

from path_chronicle.utils import get_package_root


def generate_paths(
    csv_name: str = "paths.csv",
    module_name: str = "paths.py",
    csv_dir_name: str = "csv",
    module_dir_name: str = "path_module",
    csv_root_dir: str | None = None,
    module_root_dir: str | None = None,
):
    """
    Generates a module for managing paths listed in a CSV file.

    This function reads paths from CSV file and creates a Python module with these paths
    as class attributes, facilitating IntelliSense support during development.

    Args:
        csv_name (str): The name of the CSV file. Default is "paths.csv".
        module_name (str): The name of the module to be generated.
                           Default is "paths.py".
        csv_dir_name (str): The name of the dir where the CSV file is located.
                            Default is "csv".
        module_dir_name (str): The name of the dir where the module will be created.
                               Default is "path_module".
        csv_root_dir (str | None): The root dir path for the CSV file.
                                   Default is None.
        module_root_dir (str | None): The root dir path for the module.
                                      Default is None.

    Raises:
        FileNotFoundError: If the specified CSV file does not exist.
    """

    csv_dir = (
        Path(csv_root_dir) / csv_dir_name
        if csv_root_dir
        else get_package_root() / csv_dir_name
    )
    csv_path = csv_dir / csv_name

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    module_dir = (
        Path(module_root_dir) / module_dir_name
        if module_root_dir
        else get_package_root() / module_dir_name
    )
    module_dir.mkdir(parents=True, exist_ok=True)
    module_path = module_dir / module_name

    with open(str(csv_path), mode="r") as file:
        reader = csv.DictReader(file)
        paths = {row["name"]: row["path"] for row in reader}

    lines = [
        "from pathlib import Path\n",
        "\n",
        "class Paths:\n",
        '    """\n',
        "    This class provides paths for various project directories and files.\n",
    ]

    lines.append('    """\n\n')

    for name, path in paths.items():
        lines.append(f"    {name} = Path('{path}')\n")

    lines.append("\n    @staticmethod\n")
    lines.append("    def get_path(name: str) -> Path:\n")
    lines.append('        """\n')
    lines.append("        Returns the Path object for the given name.\n\n")
    lines.append("        Available paths:\n")

    for name, path in paths.items():
        lines.append(f"        - {name}: {path}\n")

    lines.append('        """\n')
    lines.append("        return getattr(Paths, name, None)\n")

    with open(str(module_path), mode="w") as file:
        file.writelines(lines)
