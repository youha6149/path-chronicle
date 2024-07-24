import csv
import os

import pytest


@pytest.fixture
def setup_csv(tmp_path):
    """
    Fixture to create a temporary CSV file for testing.

    Args:
        tmp_path (Path): Temporary directory path provided by pytest.

    Returns:
        Path: The path to the created temporary CSV file.
    """
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_file = csv_dir / "test_paths.csv"
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "path", "description"])
    return csv_file


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
