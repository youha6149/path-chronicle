import os
import subprocess
from pathlib import Path

from path_chronicle.schema import PathEntry

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def run_command(command, cwd=None):
    """
    Run a shell command and assert it completes successfully.

    Args:
        command (str): The command to run.
        cwd (str, optional): The directory to run the command in.

    Returns:
        str: The standard output and error of the command.

    Raises:
        AssertionError: If the command returns a non-zero exit code.
    """
    result = subprocess.run(
        command, shell=True, text=True, capture_output=True, cwd=cwd
    )
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print("Standard Output:")
        print(result.stdout)
        print("Standard Error:")
        print(result.stderr)
        assert (
            result.returncode == 0
        ), f"Command failed with exit code {result.returncode}"
    return result.stdout + result.stderr


def test_create_dir_entry(setup_csv_header_only, setup_env):
    """
    Test the creation of a directory via the command line entry point.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The directory should be created and the output should indicate success.
    """
    command = f"poetry run pcmkdir test_dir {setup_env} --description 'Test directory' --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}"
    output = run_command(command, cwd=PROJECT_ROOT)
    assert "Path created at" in output
    assert os.path.exists(os.path.join(setup_env, "test_dir"))


def test_create_file_entry(setup_csv_header_only, setup_env):
    """
    Test the creation of a file via the command line entry point.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The file should be created and the output should indicate success.
    """
    command = f"poetry run pctouch test_file.txt {setup_env} --description 'Test file' --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}"
    output = run_command(command, cwd=PROJECT_ROOT)
    assert "Path created at" in output
    assert os.path.exists(os.path.join(setup_env, "test_file.txt"))


def test_list_paths_entry(setup_csv_header_only, setup_env):
    """
    Test listing paths via the command line entry point.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The output should contain the headers and the created paths.
    """
    run_command(
        f"poetry run pcmkdir test_dir {setup_env} --description 'Test directory' --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}",
        cwd=PROJECT_ROOT,
    )
    run_command(
        f"poetry run pctouch test_file.txt {setup_env} --description 'Test file' --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}",
        cwd=PROJECT_ROOT,
    )

    command = f"poetry run pcpathslist --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}"
    output = run_command(command, cwd=PROJECT_ROOT)

    lines = output.split("\n")
    expected_headers = list(PathEntry.__annotations__.keys())
    for header in expected_headers:
        assert (
            header in lines[0]
        ), f"Expected header '{header}' not found in output: {lines[0]}"
    assert any("test_dir" in line for line in lines)
    assert any("test_file.txt" in line for line in lines)


def test_remove_path_entry(setup_csv_header_only, setup_env):
    """
    Test removing paths via the command line entry point.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The directory and file should be removed and the output should indicate success.
    """
    run_command(
        f"poetry run pcmkdir test_dir {setup_env} --description 'Test directory' --csv_name {setup_csv_header_only.name} --csv_dir_name csv --csv_root_dir {setup_env} --config_root_dir {setup_env}",
        cwd=PROJECT_ROOT,
    )

    command = f"poetry run pcrmpath --name test_dir --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}"

    output = run_command(command, cwd=PROJECT_ROOT)

    assert "Path deleted:" in output, "Should indicate that the dir was deleted."
    assert not os.path.exists(os.path.join(setup_env, "test_dir"))

    run_command(
        f"poetry run pctouch test_file.txt {setup_env} --description 'Test file' --csv_name {setup_csv_header_only.name} --csv_dir_name csv --csv_root_dir {setup_env} --config_root_dir {setup_env}",
        cwd=PROJECT_ROOT,
    )

    command = f"poetry run pcrmpath --name test_file.txt --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}"
    output = run_command(command, cwd=PROJECT_ROOT)
    assert "Path deleted:" in output, "Should indicate that the file was deleted."
    assert not os.path.exists(os.path.join(setup_env, "test_file.txt"))


def test_generate_paths_entry(setup_csv_header_only, setup_env):
    """
    Test generating paths via the command line entry point.

    Args:
        setup_csv_header_only (Path): The path to the header only temporary CSV file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The generated paths.py file should contain the paths and the output should indicate success.
    """
    run_command(
        f"poetry run pcmkdir test_dir {setup_env} --description 'Test directory' --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}",
        cwd=PROJECT_ROOT,
    )

    run_command(
        f"poetry run pctouch test_file.txt {setup_env} --description 'Test file' --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --config_root_dir {setup_env}",
        cwd=PROJECT_ROOT,
    )

    command = f"poetry run gpaths --csv_name {setup_csv_header_only.name} --csv_root_dir {setup_env} --csv_dir_name csv --module_name paths.py --module_root_dir {setup_env} --module_dir_name path_module"
    run_command(command, cwd=PROJECT_ROOT)

    assert os.path.exists(
        setup_env / "path_module" / "paths.py"
    ), f"File {setup_env / 'path_module' / 'paths.py'} does not exist"


def test_set_pj_root_entry(setup_config_file, setup_env):
    """
    Test setting the project root directory via the command line entry point.

    Args:
        setup_config_file (Path): Path to the setup config file.
        setup_env (Path): The temporary environment directory.

    Asserts:
        The project root directory should be set and the output should indicate success.
    """
    test_project_root_path = str(setup_env)

    command = (
        f"poetry run pcsetpjroot {test_project_root_path} --config_root_dir {setup_env}"
    )
    run_command(command, cwd=PROJECT_ROOT)

    with open(setup_config_file, "r") as file:
        content = file.read()
        assert "project_root" in content
        assert test_project_root_path in content
