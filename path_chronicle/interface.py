import argparse
import os
import sys
from pathlib import Path

from path_chronicle.config import Config
from path_chronicle.fso_expansion import FsoExpansion
from path_chronicle.generate_paths import generate_paths


def _common_parser(description: str) -> argparse.ArgumentParser:
    """
    Creates and returns a common argument parser for directory and file creation commands.

    Args:
        description (str): A description for the parser, explaining the command's purpose.

    Returns:
        argparse.ArgumentParser: The configured argument parser.

    Arguments:
        path (str): Name of the directory or file to create.
        --description (str): Description for the directory or file. Default is an empty string.
        --csv_name (str): Name of the CSV file for storing paths. Default is "paths.csv".
        --csv_root_dir (str | None): Root directory where the CSV file will be stored. Default is None.
        --csv_dir_name (str): Name of the directory containing the CSV file. Default is "csv".
        --no-save (bool): Do not save the path to the CSV file. If specified, the path will not be saved.
        --config_root_dir (str | None): Root directory where the config file is located. Default is None.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("path", help="Name of the directory or file to create")
    parser.add_argument(
        "--description", default="", help="Description for the directory or file"
    )
    parser.add_argument(
        "--csv_name", default="paths.csv", help="Name of the CSV file for storing paths"
    )
    parser.add_argument(
        "--csv_root_dir",
        help="Root directory where the CSV file will be stored",
        default=None,
    )
    parser.add_argument(
        "--csv_dir_name",
        default="csv",
        help="Name of the directory containing the CSV file",
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Do not save the path to the CSV file"
    )
    parser.add_argument(
        "--config_root_dir",
        default=None,
        help="Root directory where the config file is located",
    )
    return parser


def _create_fso_expansion(args: argparse.Namespace) -> FsoExpansion:
    """
    Creates an FsoExpansion object based on the command line arguments.

    Args:
        args (argparse.Namespace): The parsed command line arguments.

    Returns:
        FsoExpansion: The FsoExpansion object.
    """
    if args.config_root_dir is not None:
        config = Config(Path(args.config_root_dir))
    else:
        config = Config()

    return FsoExpansion(
        config=config,
        csv_name=args.csv_name,
        csv_root_dir=args.csv_root_dir,
        csv_dir_name=args.csv_dir_name,
    )


def create_dir_and_save_csv_entry():
    """
    Create a directory and optionally saves the path info to the CSV file.

    Example usage:
        poetry run pcmkdir ./my_temp_directory --description "Temporary directory for storage"
    """
    try:
        parser = _common_parser("Create a directory.")
        args = parser.parse_args()

        pm = _create_fso_expansion(args)
        is_save_to_csv = not args.no_save
        pm.create_dir_and_save_csv(args.path, args.description, is_save_to_csv)

    except Exception as e:
        print(f"Error in create_dir_and_save_csv_entry function: {e}", file=sys.stderr)


def create_file_and_save_csv_entry():
    """
    Create a file and optionally saves the path info to the CSV file.

    Example usage:
        poetry run pctouch ./my_temp_directory/another_file.txt --description "Another file for testing"
    """
    try:
        parser = _common_parser("Create a file.")
        args = parser.parse_args()

        pm = _create_fso_expansion(args)
        is_save_to_csv = not args.no_save
        pm.create_file_and_save_csv(args.path, args.description, is_save_to_csv)

    except Exception as e:
        print(f"Error in create_file_and_save_csv_entry function: {e}", file=sys.stderr)


def list_paths_entry():
    """
    List all paths stored in the CSV file.

    Example usage:
        poetry run pcpathslist
    """
    try:
        parser = argparse.ArgumentParser(
            description="List all paths stored in the CSV file."
        )
        parser.add_argument(
            "--csv_name",
            default="paths.csv",
            help="Name of the CSV file for storing paths",
        )
        parser.add_argument(
            "--csv_root_dir",
            help="Root directory where the CSV file is stored",
            default=None,
        )
        parser.add_argument(
            "--csv_dir_name",
            default="csv",
            help="Name of the directory containing the CSV file",
        )
        parser.add_argument(
            "--config_root_dir",
            default=None,
            help="Name of the directory containing the CSV file",
        )

        args = parser.parse_args()

        pm = _create_fso_expansion(args)
        pm.list_paths()

    except Exception as e:
        print(f"Error in list_paths_entry function: {e}", file=sys.stderr)


def remove_path_and_from_csv_entry():
    """
    Remove a path based on ID, name, or path.
    and also removes it from the CSV file.

    Example usage:
        poetry run pcrmpath --id 1
        poetry run pcrmpath --name example_name
        poetry run pcrmpath --path /example/path/to/delete
    """
    try:
        parser = argparse.ArgumentParser(
            description="Remove a path based on ID, name, or path."
        )
        parser.add_argument("--id", type=int, help="ID of the path to remove")
        parser.add_argument("--name", help="Name of the path to remove")
        parser.add_argument("--path", help="Path to remove")
        parser.add_argument(
            "--csv_name",
            default="paths.csv",
            help="Name of the CSV file for storing paths",
        )
        parser.add_argument(
            "--csv_root_dir",
            help="Root directory where the CSV file is stored",
            default=None,
        )
        parser.add_argument(
            "--csv_dir_name",
            default="csv",
            help="Name of the directory containing the CSV file",
        )
        parser.add_argument(
            "--config_root_dir",
            default=None,
            help="Name of the directory containing the CSV file",
        )
        args = parser.parse_args()

        if args.id is None and args.name is None and args.path is None:
            print("Error: At least one of --id, --name, or --path must be provided.")
            return

        pm = _create_fso_expansion(args)
        pm.remove_path_and_from_csv(id=args.id, name=args.name, path=args.path)

    except Exception as e:
        print(
            f"Error in remove_path_entry function: {e}",
            file=sys.stderr,
        )


def generate_paths_entry():
    """
    Generate a Python file with paths for project directories and files.

    Example usage:
        poetry run gpaths
        poetry run gpaths --csv_root_dir ./csv --module_root_dir ./path_module --module_name paths.py
    """
    try:
        parser = argparse.ArgumentParser(
            description="Generate a Python file with paths for various project directories and files."
        )
        parser.add_argument(
            "--csv_name",
            default="paths.csv",
            help="Name of the CSV file containing paths",
        )
        parser.add_argument(
            "--csv_dir_name",
            default="csv",
            help="Name of the directory containing the CSV file",
        )
        parser.add_argument(
            "--csv_root_dir",
            help="Root directory where the CSV file is located",
            default=None,
        )
        parser.add_argument(
            "--module_name",
            default="path_archives.py",
            help="Name of the output Python file",
        )
        parser.add_argument(
            "--module_dir_name",
            default="path_module",
            help="Name of the directory to save the module file",
        )
        parser.add_argument(
            "--module_root_dir",
            help="Root directory where the output Python file will be saved",
            default=None,
        )

        args = parser.parse_args()

        generate_paths(
            csv_name=args.csv_name,
            module_name=args.module_name,
            csv_dir_name=args.csv_dir_name,
            module_dir_name=args.module_dir_name,
            csv_root_dir=args.csv_root_dir,
            module_root_dir=args.module_root_dir,
        )

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


def set_project_root_entry():
    """
    Set the project root directory to config file.

    Example usage:
        poetry run pcsetpjroot ./
        poetry run pcsetpjroot /path/to/project
    """
    try:
        parser = argparse.ArgumentParser(
            description="Set the project root directory to config file."
        )
        parser.add_argument("value", help="The value to set")
        parser.add_argument(
            "--config_root_dir",
            default=None,
            help="Root directory where the config file is located",
        )
        args = parser.parse_args()

        if args.config_root_dir is not None:
            config_root_dir = Path(args.config_root_dir)
            config = Config(config_root_dir)
        else:
            config = Config()

        config.set_project_root(args.value)

    except Exception as e:
        print(f"Error in set_project_root_entry function: {e}", file=sys.stderr)


def edit_csv_to_add_path_entry():
    """
    Add a path to the CSV file.

    Example usage:
        poetry run pcaddtocsv ./my_temp_directory --description "Temporary directory for storage"
    """
    try:
        parser = _common_parser("Add a path to the CSV file.")
        args = parser.parse_args()

        pm = _create_fso_expansion(args)
        pm.edit_csv_to_add_path(args.path, args.description)

    except Exception as e:
        print(f"Error in add_path_to_csv_entry function: {e}", file=sys.stderr)


def edit_csv_to_remove_path_entry():
    """
    Remove a path from the CSV file.

    Example usage:
        poetry run pcrmtocsv --id 1
        poetry run pcrmtocsv --name example_name
        poetry run pcrmtocsv --path /example/path/to/delete
    """
    try:
        parser = argparse.ArgumentParser(
            description="Remove a path from the CSV file based on ID, name, or path."
        )
        parser.add_argument("--id", type=int, help="ID of the path to remove")
        parser.add_argument("--name", help="Name of the path to remove")
        parser.add_argument("--path", help="Path to remove")
        parser.add_argument(
            "--csv_name",
            default="paths.csv",
            help="Name of the CSV file for storing paths",
        )
        parser.add_argument(
            "--csv_root_dir",
            help="Root directory where the CSV file is stored",
            default=None,
        )
        parser.add_argument(
            "--csv_dir_name",
            default="csv",
            help="Name of the directory containing the CSV file",
        )
        parser.add_argument(
            "--config_root_dir",
            default=None,
            help="Name of the directory containing the CSV file",
        )
        args = parser.parse_args()

        if args.id is None and args.name is None and args.path is None:
            print("Error: At least one of --id, --name, or --path must be provided.")
            return

        pm = _create_fso_expansion(args)
        pm.edit_csv_to_remove_path(id=args.id, name=args.name, path=args.path)

    except Exception as e:
        print(
            f"Error in remove_path_from_csv_entry function: {e}",
            file=sys.stderr,
        )
