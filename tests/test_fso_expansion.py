import csv
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from path_chronicle.config import Config
from path_chronicle.fso_expansion import FsoExpansion
from path_chronicle.schema import PathEntry


def create_fso_expansion(csv_name: str, setup_env: Path) -> FsoExpansion:
    config = Config(setup_env)
    return FsoExpansion(
        config=config,
        csv_name=csv_name,
        csv_root_dir=str(setup_env),
        csv_dir_name="csv",
    )


@pytest.mark.parametrize(
    "csv_name, expected_paths",
    [
        ("empty.csv", []),
        ("nonexists.csv", []),
        ("header_only.csv", []),
    ],
)
def test_load_paths_return_empty_paths_list(
    setup_env: Path,
    setup_empty_csv: Path,
    setup_csv_header_only: Path,
    csv_name: str,
    expected_paths: list[dict],
) -> None:
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

    pm = create_fso_expansion(csv_path, setup_env)

    assert (
        pm.paths == expected_paths
    ), f"Paths list should be {expected_paths} for {csv_name}."


def test_load_paths_invalid_header(setup_empty_csv: Path, setup_env: Path) -> None:
    """
    Test that load_paths correctly handles a CSV file with an invalid header.

    Args:
        setup_empty_csv (Path): The path to the temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The output should indicate that the CSV header is invalid.
    """
    with open(setup_empty_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["invalid_header"])

    with pytest.raises(ValueError, match="Invalid header in CSV file."):
        create_fso_expansion(setup_empty_csv.name, setup_env)


def test_load_paths_with_data(
    setup_csv_1_data: Path, setup_env: Path, setup_test_dir_paths: list[PathEntry]
) -> None:
    """
    Test that FsoExpansion correctly loads path data from a CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.
        setup_test_dir_paths (list): List of PathEntry objects containing
                                     the test directory paths.

    Asserts:
        The paths list should contain the loaded data.
    """
    pm = create_fso_expansion(setup_csv_1_data.name, setup_env)

    assert len(pm.paths) == 1, "Paths list should contain one entry."
    assert (
        pm.paths[0].name == setup_test_dir_paths[0].name
    ), "Name should match the CSV data."
    assert (
        pm.paths[0].path == setup_test_dir_paths[0].path
    ), "Path should match the CSV data."
    assert (
        pm.paths[0].description == setup_test_dir_paths[0].description
    ), "Description should match the CSV data."


def test_create_dir_and_save_csv(setup_csv_header_only: Path, setup_env: Path) -> None:
    """
    Test that FsoExpansion can create a directory and save its path to the CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The directory should be created and the path should be saved to the CSV file.
    """
    pm = create_fso_expansion(setup_csv_header_only.name, setup_env)
    new_dir = pm.create_dir_and_save_csv(
        "test_dir", str(setup_env), "Test directory description"
    )

    assert new_dir is not None, "new_dir should not be None."
    assert new_dir.exists() and new_dir.is_dir(), "Directory should be created."
    assert (
        pm.paths[-1].name == "test_dir"
    ), "Path name should be saved in the paths list."
    assert pm.paths[-1].path == str(new_dir), "Path should be saved in the paths list."
    assert (
        pm.paths[-1].description == "Test directory description"
    ), "Description should be saved in the paths list."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows[0]["name"] == "test_dir", "CSV should contain the directory name."
        assert rows[0]["path"] == str(new_dir), "CSV should contain the correct path."
        assert (
            rows[0]["description"] == "Test directory description"
        ), "CSV should contain the correct description."


def test_create_file_and_save_csv(setup_csv_header_only: Path, setup_env: Path) -> None:
    """
    Test that FsoExpansion can create a file and save its path to the CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The file should be created and the path should be saved to the CSV file.
    """
    pm = create_fso_expansion(setup_csv_header_only.name, setup_env)
    new_file = pm.create_file_and_save_csv(
        "test_file.txt", str(setup_env), "Test file description"
    )

    assert new_file is not None, "new_file should not be None."
    assert new_file.exists() and new_file.is_file(), "File should be created."
    assert (
        pm.paths[-1].name == new_file.name
    ), "Path name should be saved in the paths list."
    assert pm.paths[-1].path == str(new_file), "Path should be saved in the paths list."
    assert (
        pm.paths[-1].description == "Test file description"
    ), "Description should be saved in the paths list."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows[0]["name"] == new_file.name, "CSV should contain the file name."
        assert rows[0]["path"] == str(new_file), "CSV should contain the correct path."
        assert (
            rows[0]["description"] == "Test file description"
        ), "CSV should contain the correct description."


def test_create_dir_no_save_csv(setup_csv_header_only: Path, setup_env: Path) -> None:
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
    pm = create_fso_expansion(setup_csv_header_only.name, setup_env)
    new_dir = pm.create_dir_and_save_csv(
        "test_dir_nosave",
        str(setup_env),
        "Test directory no save",
        is_save_to_csv=False,
    )

    assert new_dir is not None, "new_dir should not be None."
    assert new_dir.exists() and new_dir.is_dir(), "Directory should be created."
    assert not any(
        p.name == "test_dir_nosave" for p in pm.paths
    ), "Path should not be saved in the paths list."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should remain empty."


def test_create_file_no_save_csv(setup_csv_header_only: Path, setup_env: Path) -> None:
    """
    Test that FsoExpansion can create a file without saving its path to the CSV file.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The file should be created but the path should not be saved to the CSV file.
    """
    pm = create_fso_expansion(setup_csv_header_only.name, setup_env)
    new_file = pm.create_file_and_save_csv(
        "test_file_nosave.txt",
        str(setup_env),
        "Test file no save",
        is_save_to_csv=False,
    )

    assert new_file is not None, "new_file should not be None."
    assert new_file.exists() and new_file.is_file(), "File should be created."
    assert not any(
        p.name == "test_file_nosave_txt" for p in pm.paths
    ), "Path should not be saved in the paths list."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 0, "CSV should remain empty."


def test_list_paths_empty(setup_csv_header_only: Path, setup_env: Path) -> None:
    """
    Test that FsoExpansion correctly lists paths when the CSV is empty.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The output should indicate no paths are saved.
    """
    pm = create_fso_expansion(setup_csv_header_only.name, setup_env)
    f = StringIO()
    with redirect_stdout(f):
        pm.list_paths()
    output = f.getvalue()
    assert "No paths saved in CSV." in output, "Should indicate no paths are saved."


def test_list_paths_with_data(
    setup_csv_1_data: Path, setup_env: Path, setup_test_dir_paths: list[PathEntry]
) -> None:
    """
    Test that FsoExpansion correctly lists paths when the CSV contains data.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.
        setup_test_dir_paths (list): List of PathEntry objects containing
                                     the test directory paths.

    Asserts:
        The output should match the expected table format.
    """
    pm = create_fso_expansion(setup_csv_1_data.name, setup_env)
    f = StringIO()

    with redirect_stdout(f):
        pm.list_paths()
    output = f.getvalue()
    headers = list(PathEntry.model_fields.keys())
    rows = [
        (
            str(setup_test_dir_paths[0].id),
            setup_test_dir_paths[0].name,
            setup_test_dir_paths[0].path,
            setup_test_dir_paths[0].description,
        )
    ]

    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell or ""))

    header_row = " | ".join(
        f"{header:{col_widths[i]}}" for i, header in enumerate(headers)
    )
    separator = "-+-".join("-" * width for width in col_widths)

    data_rows = "\n".join(
        " | ".join(f"{cell:{col_widths[i]}}" for i, cell in enumerate(row))
        for row in rows
    )

    expected_output = f"{header_row}\n{separator}\n{data_rows}\n\n"
    assert (
        output == expected_output
    ), f"Output should match expected table format:\n{output}"


def test_remove_dir_and_from_csv_with_subfiles(
    setup_csv_header_only: Path, setup_env: Path
) -> None:
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

    pm = create_fso_expansion(setup_csv_header_only.name, setup_env)
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


@pytest.mark.parametrize(
    "remove_by, value, expected_paths",
    [
        ("id", 1, []),
        ("name", "test_name", []),
        ("path", "test_path", []),
    ],
)
def test_remove_path_and_from_csv_all_arguments(
    setup_csv_header_only: Path,
    setup_env: Path,
    remove_by: str,
    value: str | int,
    expected_paths: list[PathEntry],
) -> None:
    """
    Test that FsoExpansion can remove a path by id, name, or path.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.
        remove_by (str): The attribute to remove by ("id", "name", or "path").
        value (str or int): The value of the attribute to remove.
        expected_paths (list): The expected list of paths.

    Asserts:
        The path should be removed from the paths list and the CSV file.
    """
    test_dir = setup_env / "test_path"
    test_dir.mkdir(parents=True, exist_ok=True)

    with open(setup_csv_header_only, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([1, "test_name", str(test_dir), "test_description"])

    pm = create_fso_expansion(setup_csv_header_only.name, setup_env)

    if remove_by == "id":
        if isinstance(value, str):
            value = int(value)
        pm.remove_path_and_from_csv(id=value)
    elif remove_by == "name":
        if isinstance(value, int):
            value = str(value)
        pm.remove_path_and_from_csv(name=value)
    elif remove_by == "path":
        pm.remove_path_and_from_csv(path=str(test_dir))

    assert (
        pm.paths == expected_paths
    ), f"Paths list should be {expected_paths} after removing the path by {remove_by}."

    with open(pm.csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert (
            rows == expected_paths
        ), f"CSV should be {expected_paths} after removing the path by {remove_by}."

    assert (
        not test_dir.exists()
    ), "The directory should be deleted from the file system."


def test_remove_path_does_not_exist_arguments(
    setup_csv_1_data: Path, setup_env: Path
) -> None:
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

    pm = create_fso_expansion(setup_csv_1_data.name, setup_env)

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


def test_remove_path_empty_paths_list(
    setup_csv_header_only: Path, setup_env: Path
) -> None:
    """
    Test that FsoExpansion empty paths list for remove path method.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The output should indicate that no processing is done
    """
    pm = create_fso_expansion(setup_csv_header_only.name, setup_env)
    f = StringIO()
    with redirect_stdout(f):
        pm.remove_path_and_from_csv(id=1)
    output = f.getvalue()

    assert pm.paths == [], "Paths list should be empty for an empty CSV."
    assert (
        "No paths available to remove.\nThe CSV file is either non-existent or empty.\n"
        == output
    ), "Should indicate that no processing is to be done"
