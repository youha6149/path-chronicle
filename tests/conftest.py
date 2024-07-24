import csv
import os
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def setup_env(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Fixture to set up the test environment by changing the current working directory.

    Args:
        tmp_path: Temporary directory path provided by pytest.

    Yields:
        The temporary directory path.
    """
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_dir)


@pytest.fixture
def setup_empty_csv(setup_env: Path) -> Path:
    """
    Fixture to create an empty CSV file for testing.

    Args:
        setup_env: Temporary directory path provided by pytest.

    Returns:
        The path to the created empty CSV file.
    """
    csv_dir = setup_env / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_file = csv_dir / "test_paths.csv"
    csv_file.touch()
    return csv_file


@pytest.fixture
def setup_csv_header_only(setup_empty_csv: Path) -> Path:
    """
    Fixture to create a header-only temporary CSV file for testing.

    Args:
        setup_empty_csv: The path to the empty CSV file.

    Returns:
        The path to the created header-only temporary CSV file.
    """

    with open(setup_empty_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "path", "description"])
    return setup_empty_csv


@pytest.fixture
def setup_csv_1_data(
    setup_csv_header_only: Path, setup_test_dir_paths: list[dict[str, str | int]]
) -> Path:
    """
    Fixture to create a header and 1 data temporary CSV file for testing.

    Args:
        setup_csv_header_only: The path to the empty CSV file.
        setup_test_dir_paths: List of dictionaries containing the test directory paths.

    Returns:
        The path to the created header and 1 data temporary CSV file.
    """

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(list(setup_test_dir_paths[0].values()))

    return setup_csv_header_only


@pytest.fixture
def setup_csv_with_variable_number_of_data(
    setup_csv_header_only: Path, setup_test_dir_paths: list[dict[str, str | int]]
) -> Path:
    """
    Fixture to create a temporary CSV file with
    variable number of data entries for testing.

    Args:
        setup_csv_header_only: The path to the header-only CSV file.
        setup_test_dir_paths: List of dictionaries containing the test directory paths.

    Returns:
        The path to the created CSV file with data entries.
    """

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        for path_data in setup_test_dir_paths:
            writer.writerow(list(path_data.values()))

    return setup_csv_header_only


@pytest.fixture
def setup_test_dir_paths(
    tmp_path: Path, request: pytest.FixtureRequest
) -> list[dict[str, str | int]]:
    """
    Fixture to create a list of test directory paths.

    Args:
        tmp_path: Temporary directory path provided by pytest.
        request: The pytest request object.

    Returns:
        A list of dictionaries containing the test directory paths.
    """
    data_cnt = request.param if hasattr(request, "param") else 1

    test_path = tmp_path / "test_dir"

    paths: list[dict[str, str | int]] = [
        {
            "id": i + 1,
            "name": f"test_dir_{i + 1}",
            "path": str(test_path),
            "description": f"test_dir_description_{i + 1}",
        }
        for i in range(data_cnt)
    ]

    return paths
