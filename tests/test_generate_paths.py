import csv

import pytest

from path_chronicle.generate_paths import generate_paths


@pytest.fixture
def setup_module_file(setup_env):
    module_dir = setup_env / "path_module"
    module_dir.mkdir(parents=True, exist_ok=True)
    module_file = module_dir / "paths.py"
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

    generate_paths(
        csv_name=setup_csv_header_only.name,
        module_name=setup_module_file.name,
        csv_root_dir=str(setup_env),
        module_root_dir=str(setup_env),
    )

    with open(setup_module_file, mode="r") as file:
        content = file.read()

    expected_content = (
        "from pathlib import Path\n"
        "\n"
        "class Paths:\n"
        '    """\n'
        "    This class provides paths for various project directories and files.\n"
        '    """\n'
        "\n"
        "\n"
        "    @staticmethod\n"
        "    def get_path(name: str) -> Path:\n"
        '        """\n'
        "        Returns the Path object for the given name.\n"
        "\n"
        "        Available paths:\n"
        '        """\n'
        "        return getattr(Paths, name, None)\n"
    )

    assert (
        content == expected_content
    ), "Generated paths.py content does not match expected content for empty CSV."


def generate_expected_content(paths: list[dict]) -> str:
    lines = [
        "from pathlib import Path\n",
        "\n",
        "class Paths:\n",
        '    """\n',
        "    This class provides paths for various project directories and files.\n",
        '    """\n',
        "\n",
    ]

    for path in paths:
        lines.append(f"    {path['name']} = Path('{path['path']}')\n")
    lines.append("\n    @staticmethod\n")
    lines.append("    def get_path(name: str) -> Path:\n")
    lines.append('        """\n')
    lines.append("        Returns the Path object for the given name.\n")
    lines.append("\n")
    lines.append("        Available paths:\n")
    for path in paths:
        lines.append(f"        - {path['name']}: {path['path']}\n")
    lines.append('        """\n')
    lines.append("        return getattr(Paths, name, None)\n")

    return "".join(lines)


def test_generate_paths_with_data(
    setup_csv_1_data, setup_test_dir_paths, setup_env, setup_module_file
) -> None:
    """
    Test the generate_paths function with a CSV file containing data.

    Args:
        setup_csv_1_data (Path): The path to the CSV file with data.
        setup_test_dir_paths (list): A list of test directory paths.
        setup_env (Path): The temporary environment directory.
        setup_module_file (Path): The path to the module file.

    Asserts:
        The generated paths.py file content should match
        the expected content for a CSV with data.
    """

    generate_paths(
        csv_name=setup_csv_1_data.name,
        module_name=setup_module_file.name,
        csv_root_dir=str(setup_env),
        module_root_dir=str(setup_env),
    )

    with open(setup_module_file, mode="r") as file:
        content = file.read()

    expected_content = generate_expected_content(setup_test_dir_paths)

    assert (
        content == expected_content
    ), "Generated paths.py content does not match expected content for CSV with data."


def test_generate_paths_with_multiple_entries(
    setup_csv_header_only, setup_env, setup_module_file
):
    """
    Test the generate_paths function with a CSV file containing multiple entries.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.
        setup_module_file (Path): The path to the module file.

    Asserts:
        The generated paths.py file content should match
        the expected content for a CSV with multiple entries.
    """
    paths = [
        {
            "id": 1,
            "name": "test_name1",
            "path": "/path/to/test1",
            "description": "Test path 1",
        },
        {
            "id": 2,
            "name": "test_name2",
            "path": "/path/to/test2",
            "description": "Test path 2",
        },
    ]
    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        for path in paths:
            writer.writerow(list(path.values()))

    generate_paths(
        csv_name=setup_csv_header_only.name,
        module_name=setup_module_file.name,
        csv_root_dir=str(setup_env),
        module_root_dir=str(setup_env),
    )

    with open(setup_module_file, mode="r") as file:
        content = file.read()

    expected_content = generate_expected_content(paths)

    assert (
        content == expected_content
    ), "Generated paths.py content doesn't match expected content for CSV with entries."
