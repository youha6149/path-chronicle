import csv
import os
import pytest

from path_chronicle.generate_paths import generate_paths

@pytest.fixture
def setup_csv(tmp_path):
    """Fixture to create a temporary CSV file for testing."""
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_file = csv_dir / "test_paths.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'path', 'description'])
    return csv_file

@pytest.fixture
def setup_env(tmp_path):
    """Fixture to set up the test environment."""
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_dir)

def test_generate_paths_empty_csv(setup_csv, setup_env):
    module_dir = setup_env / "path_module"
    module_dir.mkdir(parents=True, exist_ok=True)
    output_file = module_dir / "paths.py"
    generate_paths(csv_name=setup_csv.name, module_name=output_file.name, csv_root_dir=str(setup_env), module_root_dir=str(module_dir.parent))

    with open(output_file, mode='r') as file:
        content = file.read()

    expected_content = (
        "from pathlib import Path\n"
        "\n"
        "class Paths:\n"
        "    \"\"\"\n"
        "    This class provides paths for various project directories and files.\n"
        "    \"\"\"\n"
        "\n"
        "\n"
        "    @staticmethod\n"
        "    def get_path(name: str) -> Path:\n"
        "        \"\"\"\n"
        "        Returns the Path object for the given name.\n"
        "\n"
        "        Available paths:\n"
        "        \"\"\"\n"
        "        return getattr(Paths, name, None)\n"
    )

    assert content == expected_content, "Generated paths.py content does not match expected content for empty CSV."

def test_generate_paths_with_data(setup_csv, setup_env):
    with open(setup_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([1, 'test_name', '/path/to/test', 'Test path'])

    module_dir = setup_env / "path_module"
    module_dir.mkdir(parents=True, exist_ok=True)
    output_file = module_dir / "paths.py"
    generate_paths(csv_name=setup_csv.name, module_name=output_file.name, csv_root_dir=str(setup_env), module_root_dir=str(module_dir.parent))

    with open(output_file, mode='r') as file:
        content = file.read()

    expected_content = (
        "from pathlib import Path\n"
        "\n"
        "class Paths:\n"
        "    \"\"\"\n"
        "    This class provides paths for various project directories and files.\n"
        "    \"\"\"\n"
        "\n"
        "    test_name = Path('/path/to/test')\n"
        "\n"
        "    @staticmethod\n"
        "    def get_path(name: str) -> Path:\n"
        "        \"\"\"\n"
        "        Returns the Path object for the given name.\n"
        "\n"
        "        Available paths:\n"
        "        - test_name: /path/to/test\n"
        "        \"\"\"\n"
        "        return getattr(Paths, name, None)\n"
    )

    assert content == expected_content, "Generated paths.py content does not match expected content for CSV with data."

def test_generate_paths_with_multiple_entries(setup_csv, setup_env):
    with open(setup_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([1, 'test_name1', '/path/to/test1', 'Test path 1'])
        writer.writerow([2, 'test_name2', '/path/to/test2', 'Test path 2'])

    module_dir = setup_env / "path_module"
    module_dir.mkdir(parents=True, exist_ok=True)
    output_file = module_dir / "paths.py"
    generate_paths(csv_name=setup_csv.name, module_name=output_file.name, csv_root_dir=str(setup_env), module_root_dir=str(module_dir.parent))

    with open(output_file, mode='r') as file:
        content = file.read()

    expected_content = (
        "from pathlib import Path\n"
        "\n"
        "class Paths:\n"
        "    \"\"\"\n"
        "    This class provides paths for various project directories and files.\n"
        "    \"\"\"\n"
        "\n"
        "    test_name1 = Path('/path/to/test1')\n"
        "    test_name2 = Path('/path/to/test2')\n"
        "\n"
        "    @staticmethod\n"
        "    def get_path(name: str) -> Path:\n"
        "        \"\"\"\n"
        "        Returns the Path object for the given name.\n"
        "\n"
        "        Available paths:\n"
        "        - test_name1: /path/to/test1\n"
        "        - test_name2: /path/to/test2\n"
        "        \"\"\"\n"
        "        return getattr(Paths, name, None)\n"
    )

    assert content == expected_content, "Generated paths.py content does not match expected content for CSV with multiple entries."
