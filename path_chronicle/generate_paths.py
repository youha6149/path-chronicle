from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from path_chronicle.schema import PathEntry, check_header, normalize_name


def generate_paths(
    project_root_str: str,
    _paths_archives_dir_name: str = "path_archives",
    _csv_name: str = "paths.csv",
    _module_name: str = "path_archives.py",
):
    """
    Generates a Python module with paths for various project directories and files.

    Args:
        project_root_str (str): The path to the project root directory.
        _paths_archives_dir_name (str): The name of the directory containing the CSV file.
        _csv_name (str): The name of the CSV file containing the paths.
        _module_name (str): The name of the generated Python module.

    Raises:
        ValueError: If the CSV file does not exist, is empty, has an invalid header, or has invalid data.
    """
    project_root = Path(project_root_str)
    paths_dir = project_root / _paths_archives_dir_name
    csv_path = paths_dir / _csv_name
    module_path = paths_dir / _module_name
    init_file_path = paths_dir / "__init__.py"

    if not csv_path.exists() or csv_path.stat().st_size == 0:
        raise ValueError(f"CSV file does not exist or is empty: {csv_path}")

    df = pd.read_csv(csv_path)
    if not check_header(df.columns.tolist()):
        raise ValueError(f"Invalid header in CSV file: {csv_path}")

    if df.empty:
        raise ValueError(f"Empty CSV file: {csv_path}")

    paths = {}
    for _, row in df.iterrows():
        try:
            row_data = row.to_dict()
            row_data["id"] = int(row_data["id"])
            row_data = {k: v if pd.notna(v) else None for k, v in row_data.items()}
            path_entry = PathEntry(**row_data)
            paths[path_entry.name] = path_entry.path
        except ValidationError as ve:
            raise ValueError(f"Validation error for row {row_data}: {ve}")

    lines = [
        "from pathlib import Path\n",
        "\n\n",
        "class PathArchives:\n",
        '    """\n',
        "    This class provides paths for various project directories and files.\n",
        '    """\n',
        "\n",
    ]

    for name, path in paths.items():
        lines.append(f"    {normalize_name(name)} = Path('{path}')\n")
    lines.append("\n    @staticmethod\n")
    lines.append("    def get_path(name: str) -> Path:\n")
    lines.append('        """\n')
    lines.append("        Returns the Path object for the given name.\n")
    lines.append("\n")
    lines.append("        Available paths:\n")
    for name, path in paths.items():
        lines.append(f"        - {normalize_name(name)}: {path}\n")
    lines.append('        """\n')
    lines.append('        return getattr(PathArchives, name, None) or Path("")\n')

    with open(str(module_path), mode="w") as file:
        file.writelines(lines)

    init_lines = [
        "import importlib.util\n",
        "import sys\n",
        "from pathlib import Path\n",
        "\n\n",
        "def load_generated_paths_module():\n",
        f'    module_path = Path(__file__).parent / "{_module_name}"\n',
        "    if not module_path.exists():\n",
        '        raise FileNotFoundError(f"Generated paths module not found: {module_path}")\n',
        "\n",
        "    spec = importlib.util.spec_from_file_location(\n",
        f'        "path_module.{_module_name.replace(".py", "")}", module_path\n',
        "    )\n",
        "    module = importlib.util.module_from_spec(spec)\n",
        f'    sys.modules["path_module.{_module_name.replace(".py", "")}"] = module\n',
        "    spec.loader.exec_module(module)\n",
        "    return module\n",
        "\n\n",
        "try:\n",
        "    paths = load_generated_paths_module()\n",
        "    PathArchives = paths.PathArchives\n",
        "except FileNotFoundError:\n",
        '    print("Generated paths module not found. Run `generate_paths` to create it.")\n',
    ]

    with open(init_file_path, mode="w") as init_file:
        init_file.writelines(init_lines)
