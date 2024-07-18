import pytest
import csv
import os

from path_chronicle.fso_expansion import FsoExpansion

@pytest.fixture
def setup_csv(tmp_path):
    """Fixture to create a temporary CSV file for testing."""
    print(tmp_path)
    csv_file = tmp_path / "test_paths.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'path'])
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
    assert pm.paths == {}, "Paths dictionary should be empty for an empty CSV."

def test_load_paths_with_data(setup_csv, setup_env):
    with open(setup_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['test_name', 'test_path'])

    pm = FsoExpansion(str(setup_csv))
    assert pm.paths['test_name'] == 'test_path', "Paths dictionary should contain the data from the CSV."

def test_create_dir(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    new_dir = pm.create_dir("test_dir", str(setup_env))
    
    assert new_dir.exists() and new_dir.is_dir(), "Directory should be created."
    assert pm.paths["test_dir"] == str(new_dir), "Path should be saved in the paths dictionary."

    with open(pm.csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows[0]['name'] == "test_dir", "CSV should contain the directory name."
        assert rows[0]['path'] == str(new_dir), "CSV should contain the correct path."

def test_create_file(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    new_file = pm.create_file("test_file.txt", str(setup_env))
    
    assert new_file.exists() and new_file.is_file(), "File should be created."
    assert pm.paths["test_file.txt"] == str(new_file), "Path should be saved in the paths dictionary."

    with open(pm.csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows[0]['name'] == "test_file.txt", "CSV should contain the file name."
        assert rows[0]['path'] == str(new_file), "CSV should contain the correct path."

def test_create_dir_no_save(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    new_dir = pm.create_dir("test_dir_nosave", str(setup_env), is_save_to_csv=False)
    
    assert new_dir.exists() and new_dir.is_dir(), "Directory should be created."
    assert "test_dir_nosave" not in pm.paths, "Path should not be saved in the paths dictionary."

    with open(pm.csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should remain empty."

def test_create_file_no_save(setup_csv, setup_env):
    pm = FsoExpansion(str(setup_csv))
    new_file = pm.create_file("test_file_nosave.txt", str(setup_env), is_save_to_csv=False)
    
    assert new_file.exists() and new_file.is_file(), "File should be created."
    assert "test_file_nosave.txt" not in pm.paths, "Path should not be saved in the paths dictionary."

    with open(pm.csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should remain empty."

