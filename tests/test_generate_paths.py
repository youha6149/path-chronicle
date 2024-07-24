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


def test_generate_paths_with_data(setup_csv_header_only, setup_env, setup_module_file):
    """
    Test the generate_paths function with a CSV file containing data.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The generated paths.py file content should match
        the expected content for a CSV with data.
    """
    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([1, "test_name", "/path/to/test", "Test path"])

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
        "    test_name = Path('/path/to/test')\n"
        "\n"
        "    @staticmethod\n"
        "    def get_path(name: str) -> Path:\n"
        '        """\n'
        "        Returns the Path object for the given name.\n"
        "\n"
        "        Available paths:\n"
        "        - test_name: /path/to/test\n"
        '        """\n'
        "        return getattr(Paths, name, None)\n"
    )

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

    Asserts:
        The generated paths.py file content should match
        the expected content for a CSV with multiple entries.
    """
    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([1, "test_name1", "/path/to/test1", "Test path 1"])
        writer.writerow([2, "test_name2", "/path/to/test2", "Test path 2"])

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
        "    test_name1 = Path('/path/to/test1')\n"
        "    test_name2 = Path('/path/to/test2')\n"
        "\n"
        "    @staticmethod\n"
        "    def get_path(name: str) -> Path:\n"
        '        """\n'
        "        Returns the Path object for the given name.\n"
        "\n"
        "        Available paths:\n"
        "        - test_name1: /path/to/test1\n"
        "        - test_name2: /path/to/test2\n"
        '        """\n'
        "        return getattr(Paths, name, None)\n"
    )

    assert (
        content == expected_content
    ), "Generated paths.py content doesn't match expected content for CSV with entries."
