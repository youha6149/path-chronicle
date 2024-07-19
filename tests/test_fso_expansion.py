import csv
from contextlib import redirect_stdout
from io import StringIO
import os
import pytest

from path_chronicle.fso_expansion import FsoExpansion

@pytest.fixture
def setup_csv(tmp_path):
    """Fixture to create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_paths.csv"
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

def test_load_paths_empty_csv(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    assert pm.paths == [], "Paths list should be empty for an empty CSV."

def test_load_paths_with_data(setup_csv, setup_env):
    with open(setup_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['1', 'test_name', 'test_path', 'test_description'])

    pm = FsoExpansion(str(setup_csv))
    assert len(pm.paths) == 1, "Paths list should contain one entry."
    assert pm.paths[0]['name'] == 'test_name', "Name should match the CSV data."
    assert pm.paths[0]['path'] == 'test_path', "Path should match the CSV data."
    assert pm.paths[0]['description'] == 'test_description', "Description should match the CSV data."

def test_create_dir(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    new_dir = pm.create_dir("test_dir", str(setup_env), "Test directory description")
    
    assert new_dir.exists() and new_dir.is_dir(), "Directory should be created."
    assert pm.paths[-1]['name'] == "test_dir", "Path name should be saved in the paths list."
    assert pm.paths[-1]['path'] == str(new_dir), "Path should be saved in the paths list."
    assert pm.paths[-1]['description'] == "Test directory description", "Description should be saved in the paths list."

    with open(pm.csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows[0]['name'] == "test_dir", "CSV should contain the directory name."
        assert rows[0]['path'] == str(new_dir), "CSV should contain the correct path."
        assert rows[0]['description'] == "Test directory description", "CSV should contain the correct description."

def test_create_file(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    new_file = pm.create_file("test_file.txt", str(setup_env), "Test file description")
    
    assert new_file.exists() and new_file.is_file(), "File should be created."
    assert pm.paths[-1]['name'] == "test_file.txt", "Path name should be saved in the paths list."
    assert pm.paths[-1]['path'] == str(new_file), "Path should be saved in the paths list."
    assert pm.paths[-1]['description'] == "Test file description", "Description should be saved in the paths list."

    with open(pm.csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows[0]['name'] == "test_file.txt", "CSV should contain the file name."
        assert rows[0]['path'] == str(new_file), "CSV should contain the correct path."
        assert rows[0]['description'] == "Test file description", "CSV should contain the correct description."

def test_create_dir_no_save(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    new_dir = pm.create_dir("test_dir_nosave", str(setup_env), "Test directory no save", is_save_to_csv=False)
    
    assert new_dir.exists() and new_dir.is_dir(), "Directory should be created."
    assert not any(p['name'] == "test_dir_nosave" for p in pm.paths), "Path should not be saved in the paths list."

    with open(pm.csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should remain empty."

def test_create_file_no_save(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    new_file = pm.create_file("test_file_nosave.txt", str(setup_env), "Test file no save", is_save_to_csv=False)
    
    assert new_file.exists() and new_file.is_file(), "File should be created."
    assert not any(p['name'] == "test_file_nosave.txt" for p in pm.paths), "Path should not be saved in the paths list."

    with open(pm.csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should remain empty."

def test_list_paths_empty(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    f = StringIO()
    with redirect_stdout(f):
        pm.list_paths()
    output = f.getvalue()
    assert "No paths saved in CSV." in output, "Should indicate no paths are saved."

def test_list_paths_with_data(setup_csv, setup_env):
    with open(setup_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['1', 'test_name', 'test_path', 'test_description'])

    pm = FsoExpansion(str(setup_csv))
    f = StringIO()
    with redirect_stdout(f):
        pm.list_paths()
    output = f.getvalue()
    expected_output = (
        "ID | Name      | Path      | Description     \n"
        "---+-----------+-----------+-----------------\n"
        "1  | test_name | test_path | test_description\n"
        "\n"
    )
    assert output == expected_output, f"Output should match expected table format:\n{output}"
