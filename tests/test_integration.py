import csv
import os
import subprocess

import pytest

# プロジェクトルートのディレクトリを指定
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def setup_csv(tmp_path):
    """Fixture to create a temporary CSV file for testing."""
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_file = csv_dir / "test_paths.csv"
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "path", "description"])
    return csv_file


@pytest.fixture
def setup_env(tmp_path):
    """Fixture to set up the test environment."""
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_dir)


def run_command(command, cwd=None):
    result = subprocess.run(
        command, shell=True, text=True, capture_output=True, cwd=cwd
    )
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(result.stdout)
        print(result.stderr)
    assert result.returncode == 0
    return result.stdout


def test_create_dir_entry(setup_csv, setup_env):
    command = f"poetry run pcmkdir test_dir {setup_env} --description 'Test directory' --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv"
    output = run_command(command, cwd=PROJECT_ROOT)
    assert "Path created at" in output
    assert os.path.exists(os.path.join(setup_env, "test_dir"))


def test_create_file_entry(setup_csv, setup_env):
    command = f"poetry run pctouch test_file.txt {setup_env} --description 'Test file' --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv"
    output = run_command(command, cwd=PROJECT_ROOT)
    assert "Path created at" in output
    assert os.path.exists(os.path.join(setup_env, "test_file.txt"))


def test_list_paths_entry(setup_csv, setup_env):
    run_command(
        f"poetry run pcmkdir test_dir {setup_env} --description 'Test directory' --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv",
        cwd=PROJECT_ROOT,
    )
    run_command(
        f"poetry run pctouch test_file.txt {setup_env} --description 'Test file' --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv",
        cwd=PROJECT_ROOT,
    )

    command = f"poetry run pcpathslist --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv"
    output = run_command(command, cwd=PROJECT_ROOT)

    lines = output.split("\n")
    expected_headers = ["ID", "Name", "Path", "Description"]
    for header in expected_headers:
        assert (
            header in lines[0]
        ), f"Expected header '{header}' not found in output: {lines[0]}"
    assert any("test_dir" in line for line in lines)
    assert any("test_file.txt" in line for line in lines)


def test_remove_path_entry(setup_csv, setup_env):
    run_command(
        f"poetry run pcmkdir test_dir {setup_env} --description 'Test directory' --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv",
        cwd=PROJECT_ROOT,
    )
    run_command(
        f"poetry run pctouch test_file.txt {setup_env} --description 'Test file' --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv",
        cwd=PROJECT_ROOT,
    )

    command = f"poetry run pcrmpath --name test_dir --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv"
    output = run_command(command, cwd=PROJECT_ROOT)
    assert "Path deleted:" in output
    assert not os.path.exists(os.path.join(setup_env, "test_dir"))

    # memo:ファイルはcsvに記録される際に"."が"."に置き換えられる
    rn_test_file_txt = "test_file.txt".replace(".", "_")
    command = f"poetry run pcrmpath --name {rn_test_file_txt} --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv"
    output = run_command(command, cwd=PROJECT_ROOT)
    assert "Path deleted:" in output
    assert not os.path.exists(os.path.join(setup_env, "test_file.txt"))


def test_generate_paths_entry(setup_csv, setup_env):
    run_command(
        f"poetry run pcmkdir test_dir {setup_env} --description 'Test directory' --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv",
        cwd=PROJECT_ROOT,
    )
    run_command(
        f"poetry run pctouch test_file.txt {setup_env} --description 'Test file' --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv",
        cwd=PROJECT_ROOT,
    )

    command = f"poetry run gpaths --csv_name {setup_csv.name} --csv_root_dir {setup_env} --csv_dir_name csv --module_name paths.py --module_root_dir {setup_env} --module_dir_name path_module"
    output = run_command(command, cwd=PROJECT_ROOT)
    assert os.path.exists(setup_env / "path_module" / "paths.py")

    with open(setup_env / "path_module" / "paths.py", "r") as file:
        content = file.read()
        assert "test_dir" in content
        assert "test_file.txt" in content

    os.remove(setup_env / "path_module" / "paths.py")
