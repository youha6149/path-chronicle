import csv
import os

import pytest


@pytest.fixture
def setup_empty_csv(tmp_path):
    """
    Fixture to create a empty CSV file for testing.

    Args:
        tmp_path (Path): Temporary directory path provided by pytest.

    Returns:
        Path: The path to the created empty CSV file.
    """
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_file = csv_dir / "test_paths.csv"

    return csv_file


@pytest.fixture
def setup_csv_header_only(setup_empty_csv):
    """
    Fixture to create a header only temporary CSV file for testing.

    Args:
        setup_empty_csv (Path): The path to the empty CSV file.

    Returns:
        Path: The path to the created header only temporary CSV file.
    """

    with open(setup_empty_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "path", "description"])
    return setup_empty_csv


@pytest.fixture
def setup_env(tmp_path):
    """
    Fixture to set up the test environment by changing the current working directory.

    Args:
        tmp_path (Path): Temporary directory path provided by pytest.

    Yields:
        Path: The temporary directory path.
    """
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_dir)
