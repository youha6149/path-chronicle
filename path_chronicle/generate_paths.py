from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from path_chronicle.schema import PathEntry, check_header, normalize_name
from path_chronicle.utils import get_package_root


def generate_paths(
    csv_name: str = "paths.csv",
    module_name: str = "path_archives.py",
    csv_dir_name: str = "csv",
    module_dir_name: str = "path_module",
    csv_root_dir: str | None = None,
    module_root_dir: str | None = None,
):
    package_root_str = get_package_root()
    if package_root_str is None:
        raise ValueError("Could not find package root directory.")

    csv_dir = (
        Path(csv_root_dir) / csv_dir_name
        if csv_root_dir is not None
        else package_root_str / csv_dir_name
    )
    csv_path = csv_dir / csv_name

    if not csv_path.exists() or csv_path.stat().st_size == 0:
        raise ValueError(f"CSV file does not exist or is empty: {csv_path}")

    module_dir = (
        Path(module_root_dir) / module_dir_name
        if module_root_dir is not None
        else package_root_str / module_dir_name
    )
    module_dir.mkdir(parents=True, exist_ok=True)
    module_path = module_dir / module_name

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

    init_file_path = module_dir / "__init__.py"
    init_lines = [
        "import importlib.util\n",
        "import sys\n",
        "from pathlib import Path\n",
        "\n\n",
        "def load_generated_paths_module():\n",
        f'    module_path = Path(__file__).parent / "{module_name}"\n',
        "    if not module_path.exists():\n",
        '        raise FileNotFoundError(f"Generated paths module not found: {module_path}")\n',
        "\n",
        "    spec = importlib.util.spec_from_file_location(\n",
        f'        "path_module.{module_name.replace(".py", "")}", module_path\n',
        "    )\n",
        "    module = importlib.util.module_from_spec(spec)\n",
        f'    sys.modules["path_module.{module_name.replace(".py", "")}"] = module\n',
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
