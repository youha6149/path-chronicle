import csv

import pytest

from path_chronicle.generate_paths import generate_paths
from path_chronicle.schema import PathEntry


@pytest.fixture
def setup_module_file(setup_env):
    module_dir = setup_env / "path_module"
    module_dir.mkdir(parents=True, exist_ok=True)
    module_file = module_dir / "path_archives.py"
    return module_file


def test_generate_paths_nonexists_csv(setup_env):
    """
    Test the generate_paths function with a non-existent CSV file.

    Args:
        setup_env (Path): The temporary environment directory.

    Asserts:
        ValueError is raised with appropriate message.
    """

    nonexists_csv_path = setup_env / "csv" / "nonexists.csv"

    with pytest.raises(
        ValueError, match=f"CSV file does not exist or is empty: {nonexists_csv_path}"
    ):
        generate_paths(
            csv_name="nonexists.csv",
            module_name="paths.py",
            csv_root_dir=str(setup_env),
            module_root_dir=str(setup_env),
        )


def test_generate_paths_empty_csv(setup_env):
    """
    Test the generate_paths function with an empty CSV file.

    Args:
        setup_env (Path): The temporary environment directory.

    Asserts:
        ValueError is raised with appropriate message.
    """

    empty_csv_dir = setup_env / "csv"
    empty_csv_dir.mkdir(parents=True, exist_ok=True)

    empty_csv_path = empty_csv_dir / "empty.csv"
    empty_csv_path.touch()

    with pytest.raises(
        ValueError, match=f"CSV file does not exist or is empty: {empty_csv_path}"
    ):
        generate_paths(
            csv_name="empty.csv",
            module_name="paths.py",
            csv_root_dir=str(setup_env),
            module_root_dir=str(setup_env),
        )


def test_generate_paths_invalid_header(setup_env, setup_empty_csv, setup_module_file):
    """
    Test the generate_paths function with a CSV file with an invalid header.

    Args:
        setup_env (Path): The temporary environment directory.

    Asserts:
        ValueError is raised with appropriate message.
    """

    with open(setup_empty_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["invalid", "header"])

    with pytest.raises(
        ValueError, match=f"Invalid header in CSV file: {setup_empty_csv}"
    ):
        generate_paths(
            csv_name=setup_empty_csv.name,
            module_name=setup_module_file.name,
            csv_root_dir=str(setup_env),
            module_root_dir=str(setup_env),
        )


def test_generate_paths_validation_error(
    setup_env, setup_csv_header_only, setup_module_file
):
    """
    Test the generate_paths function with a CSV file containing invalid data.

    Args:
        setup_env (Path): The temporary environment directory.
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_module_file (Path): The path to the module file.

    Asserts:
        ValueError is raised with appropriate message.
    """

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["-1", "", "", ""])

    with pytest.raises(ValueError, match="Validation error for row"):
        generate_paths(
            csv_name=setup_csv_header_only.name,
            module_name=setup_module_file.name,
            csv_root_dir=str(setup_env),
            module_root_dir=str(setup_env),
        )


def test_generate_paths_empty_data(setup_csv_header_only, setup_env, setup_module_file):
    """
    Test the generate_paths function with an empty data in CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.
        setup_module_file (Path): The path to the module file.

    Asserts:
        The generated paths.py file content should match
        the expected content for an empty CSV.
    """

    with pytest.raises(ValueError, match=f"Empty CSV file: {setup_csv_header_only}"):
        generate_paths(
            csv_name=setup_csv_header_only.name,
            module_name=setup_module_file.name,
            csv_root_dir=str(setup_env),
            module_root_dir=str(setup_env),
        )


def generate_expected_content_for_path_archives(paths: list[PathEntry]) -> str:
    lines = [
        "from pathlib import Path\n",
        "\n",
        "class PathArchives:\n",
        '    """\n',
        "    This class provides paths for various project directories and files.\n",
        '    """\n',
        "\n",
    ]

    for path in paths:
        lines.append(f"    {path.name} = Path('{path.path}')\n")
    lines.append("\n    @staticmethod\n")
    lines.append("    def get_path(name: str) -> Path:\n")
    lines.append('        """\n')
    lines.append("        Returns the Path object for the given name.\n")
    lines.append("\n")
    lines.append("        Available paths:\n")
    for path in paths:
        lines.append(f"        - {path.name}: {path.path}\n")
    lines.append('        """\n')
    lines.append('        return getattr(PathArchives, name, None) or Path("")\n')

    return "".join(lines)


def generate_expected_init_content(module_name: str) -> str:
    lines = [
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
    return "".join(lines)


@pytest.mark.parametrize("setup_test_dir_paths", [1, 2, 3], indirect=True)
def test_generate_paths_with_variable_data(
    setup_csv_with_variable_number_of_data,
    setup_test_dir_paths: list[PathEntry],
    setup_env,
    setup_module_file,
) -> None:
    """
    Test the generate_paths function with a
    CSV file containing variable number of data entries.

    Args:
        setup_csv_with_variable_number_of_data (Path): The path to the
                                                       CSV file with data.
        setup_test_dir_paths (list): A list of test directory paths.
        setup_env (Path): The temporary environment directory.
        setup_module_file (Path): The path to the module file.

    Asserts:
        The generated paths.py file content should match
        the expected content for a CSV with data.
    """

    generate_paths(
        csv_name=setup_csv_with_variable_number_of_data.name,
        module_name=setup_module_file.name,
        csv_root_dir=str(setup_env),
        module_root_dir=str(setup_env),
    )

    with open(setup_module_file, mode="r") as file:
        content = file.read()

    expected_content = generate_expected_content_for_path_archives(setup_test_dir_paths)

    assert (
        content.strip() == expected_content.strip()
    ), "Generated paths.py content does not match expected content for CSV with data."

    init_file_path = setup_module_file.parent / "__init__.py"

    with open(init_file_path, mode="r") as init_file:
        init_content = init_file.read()

    expected_init_content = generate_expected_init_content(setup_module_file.name)

    assert (
        init_content.strip() == expected_init_content.strip()
    ), "__init__.py content does not match expected content."
