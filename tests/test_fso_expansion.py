import csv
from contextlib import redirect_stdout
from io import StringIO

import pytest

from path_chronicle.fso_expansion import FsoExpansion


@pytest.mark.parametrize(
    "csv_name, expected_paths",
    [
        ("empty.csv", []),
        ("nonexists.csv", []),
        ("header_only.csv", []),
    ],
)
def test_load_paths_return_empty_paths_list(
    setup_env, setup_empty_csv, setup_csv_header_only, csv_name, expected_paths
):
    """
    Test that load_paths correctly handles a CSV scenario
    where it should return an empty paths list.

    Args:
        setup_env (Path): The temporary environment directory.
        setup_empty_csv (Path): The path to the temporary CSV file.
        setup_csv_header_only (Path): The path to the temporary header-only CSV file.
        csv_name (str): The name of the CSV file to test.
        expected_paths (list): The expected list of paths.

    Asserts:
        The paths list should match the expected paths.
    """
    if csv_name == "empty.csv":
        csv_path = setup_empty_csv.name
    elif csv_name == "header_only.csv":
        csv_path = setup_csv_header_only.name
    else:
        csv_path = csv_name

    pm = FsoExpansion(
        csv_name=csv_path, csv_root_dir=str(setup_env), csv_dir_name="csv"
    )
    assert (
        pm.paths == expected_paths
    ), f"Paths list should be {expected_paths} for {csv_name}."


def test_load_paths_with_data(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion correctly loads path data from a CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The paths list should contain the loaded data.
    """
    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["1", "test_name", "test_path", "test_description"])

    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    assert len(pm.paths) == 1, "Paths list should contain one entry."
    assert pm.paths[0]["name"] == "test_name", "Name should match the CSV data."
    assert pm.paths[0]["path"] == "test_path", "Path should match the CSV data."
    assert (
        pm.paths[0]["description"] == "test_description"
    ), "Description should match the CSV data."


def test_create_dir_and_save_csv(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion can create a directory and save its path to the CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The directory should be created and the path should be saved to the CSV file.
    """
    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    new_dir = pm.create_dir_and_save_csv(
        "test_dir", str(setup_env), "Test directory description"
    )

    assert new_dir.exists() and new_dir.is_dir(), "Directory should be created."
    assert (
        pm.paths[-1]["name"] == "test_dir"
    ), "Path name should be saved in the paths list."
    assert pm.paths[-1]["path"] == str(
        new_dir
    ), "Path should be saved in the paths list."
    assert (
        pm.paths[-1]["description"] == "Test directory description"
    ), "Description should be saved in the paths list."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows[0]["name"] == "test_dir", "CSV should contain the directory name."
        assert rows[0]["path"] == str(new_dir), "CSV should contain the correct path."
        assert (
            rows[0]["description"] == "Test directory description"
        ), "CSV should contain the correct description."


def test_create_file_and_save_csv(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion can create a file and save its path to the CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The file should be created and the path should be saved to the CSV file.
    """
    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    new_file = pm.create_file_and_save_csv(
        "test_file.txt", str(setup_env), "Test file description"
    )

    rn_filename = "test_file_txt"

    assert new_file.exists() and new_file.is_file(), "File should be created."
    assert (
        pm.paths[-1]["name"] == rn_filename
    ), "Path name should be saved in the paths list."
    assert pm.paths[-1]["path"] == str(
        new_file
    ), "Path should be saved in the paths list."
    assert (
        pm.paths[-1]["description"] == "Test file description"
    ), "Description should be saved in the paths list."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows[0]["name"] == rn_filename, "CSV should contain the file name."
        assert rows[0]["path"] == str(new_file), "CSV should contain the correct path."
        assert (
            rows[0]["description"] == "Test file description"
        ), "CSV should contain the correct description."


def test_create_dir_no_save_csv(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion can create a directory without saving
    its path to the CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The directory should be created but
        the path should not be saved to the CSV file.
    """
    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    new_dir = pm.create_dir_and_save_csv(
        "test_dir_nosave",
        str(setup_env),
        "Test directory no save",
        is_save_to_csv=False,
    )

    assert new_dir.exists() and new_dir.is_dir(), "Directory should be created."
    assert not any(
        p["name"] == "test_dir_nosave" for p in pm.paths
    ), "Path should not be saved in the paths list."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should remain empty."


def test_create_file_no_save_csv(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion can create a file without saving its path to the CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The file should be created but the path should not be saved to the CSV file.
    """
    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    new_file = pm.create_file_and_save_csv(
        "test_file_nosave.txt",
        str(setup_env),
        "Test file no save",
        is_save_to_csv=False,
    )

    assert new_file.exists() and new_file.is_file(), "File should be created."
    assert not any(
        p["name"] == "test_file_nosave_txt" for p in pm.paths
    ), "Path should not be saved in the paths list."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should remain empty."


def test_list_paths_empty(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion correctly lists paths when the CSV is empty.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The output should indicate no paths are saved.
    """
    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    f = StringIO()
    with redirect_stdout(f):
        pm.list_paths()
    output = f.getvalue()
    assert "No paths saved in CSV." in output, "Should indicate no paths are saved."


def test_list_paths_with_data(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion correctly lists paths when the CSV contains data.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The output should match the expected table format.
    """
    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["1", "test_name", "test_path", "test_description"])

    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
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
    assert (
        output == expected_output
    ), f"Output should match expected table format:\n{output}"


def test_remove_dir_and_from_csv_with_subfiles(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion can remove a directory and its subfiles.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The directory and its subfiles should be removed,
        and the paths list should be empty.
    """
    test_dir = setup_env / "test_dir"
    test_dir.mkdir(parents=True, exist_ok=True)
    sub_file = test_dir / "sub_file.txt"
    sub_file.touch()

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["1", "test_dir", str(test_dir), "test directory"])
        writer.writerow(["2", "sub_file", str(sub_file), "sub file"])

    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    pm.remove_path_and_from_csv(path=str(test_dir))

    assert (
        len(pm.paths) == 0
    ), "Paths list should be empty after removing the directory with subfiles."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert (
            len(rows) == 0
        ), "CSV should be empty after removing the directory with subfiles."


def test_remove_path_and_from_csv_by_id(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion can remove a path by ID.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The path should be removed from the paths list and the CSV file.
    """
    test_dir = setup_env / "test_path"
    test_dir.mkdir(parents=True, exist_ok=True)

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["1", "test_name", str(test_dir), "test_description"])

    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    pm.remove_path_and_from_csv(id=1)

    assert (
        len(pm.paths) == 0
    ), "Paths list should be empty after removing the path by ID."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should be empty after removing the path by ID."


def test_remove_path_and_from_csv_by_name(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion can remove a path by name.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The path should be removed from the paths list and the CSV file.
    """
    test_dir = setup_env / "test_path"
    test_dir.mkdir(parents=True, exist_ok=True)

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["1", "test_name", str(test_dir), "test_description"])

    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    pm.remove_path_and_from_csv(name="test_name")

    assert (
        len(pm.paths) == 0
    ), "Paths list should be empty after removing the path by name."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should be empty after removing the path by name."


def test_remove_path_and_from_csv_by_path(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion can remove a path by path.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The path should be removed from the paths list and the CSV file.
    """
    test_dir = setup_env / "test_path"
    test_dir.mkdir(parents=True, exist_ok=True)

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["1", "test_name", str(test_dir), "test_description"])

    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    pm.remove_path_and_from_csv(path=str(test_dir))

    assert (
        len(pm.paths) == 0
    ), "Paths list should be empty after removing the path by path."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should be empty after removing the path by path."


def test_remove_path_does_not_exist_arguments(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion handles attempts to remove nonexistent paths.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The output should indicate that no path was found with the given identifier.
    """

    test_dir = setup_env / "test_path"
    test_dir.mkdir(parents=True, exist_ok=True)

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["1", "test_name", str(test_dir), "test_description"])

    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )

    f = StringIO()
    with redirect_stdout(f):
        pm.remove_path_and_from_csv(id=999)
    output = f.getvalue()

    assert (
        "No path found with id: 999" in output
    ), "Should indicate no path found with given ID."

    with redirect_stdout(f):
        pm.remove_path_and_from_csv(name="nonexistent_name")
    output = f.getvalue()
    assert (
        "No path found with name: nonexistent_name" in output
    ), "Should indicate no path found with given name."

    with redirect_stdout(f):
        pm.remove_path_and_from_csv(path="/nonexistent/path")
    output = f.getvalue()
    assert (
        "No path found with path: /nonexistent/path" in output
    ), "Should indicate no path found with given path."


def test_remove_path_empty_paths_list(setup_csv_header_only, setup_env):
    """
    Test that FsoExpansion empty paths list for remove path method.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The output should indicate that no processing is done
    """

    pm = FsoExpansion(
        csv_name=setup_csv_header_only.name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )
    f = StringIO()
    with redirect_stdout(f):
        pm.remove_path_and_from_csv(id=1)
    output = f.getvalue()

    assert pm.paths == [], "Paths list should be empty for an empty CSV."
    assert (
        "No paths available to remove.\nThe CSV file is either non-existent or empty.\n"
        == output
    ), "Should indicate that no processing is to be done"
