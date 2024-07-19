import argparse
import sys

from path_chronicle.fso_expansion import FsoExpansion


def _common_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('name', help='Name of the directory or file to create')
    parser.add_argument('parent_dir', help='Parent directory where the directory or file will be created')
    parser.add_argument('--description', default='', help='Description for the directory or file')
    parser.add_argument('--csv', default='paths.csv', help='Name of the CSV file for storing paths')
    parser.add_argument('--no-save', action='store_true', help='Do not save the path to the CSV file')
    return parser

def create_dir_entry():
    """
    ex:
        poetry run pcmkdir my_temp_directory ./ --description "Temporary directory for storage"
    """
    
    try:
        parser = _common_parser('Create a directory.')
        args = parser.parse_args()

        pm = FsoExpansion(args.csv)
        is_save_to_csv = not args.no_save
        pm.create_dir(args.name, args.parent_dir, args.description, is_save_to_csv)

    except Exception as e:
        print(f"Error in create_dir_entry function: {e}", file=sys.stderr)

def create_file_entry():
    """
    ex:
        poetry run pctouch another_file.txt my_temp_directory --description "Another file for testing"
    """

    try:
        parser = _common_parser('Create a file.')
        args = parser.parse_args()

        pm = FsoExpansion(args.csv)
        is_save_to_csv = not args.no_save
        pm.create_file(args.name, args.parent_dir, args.description, is_save_to_csv)

    except Exception as e:
        print(f"Error in create_file_entry function: {e}", file=sys.stderr)

def list_paths_entry():
    """
    ex:
        poetry run pcpathslist
    """

    try:
        parser = argparse.ArgumentParser(description='List all paths stored in the CSV file.')
        parser.add_argument('--csv', default='paths.csv', help='Name of the CSV file for storing paths')
        args = parser.parse_args()

        pm = FsoExpansion(args.csv)
        pm.list_paths()

    except Exception as e:
        print(f"Error in list_paths_entry function: {e}", file=sys.stderr)

def remove_path_entry():
    """
    ex:
        poetry run pcrmpath --id 1
        poetry run pcrmpath --name example_name
        poetry run pcrmpath --path /example/path/to/delete
    """
    
    try:
        parser = argparse.ArgumentParser(description='Remove a path based on id, name, or path.')
        parser.add_argument('--id', type=int, help='ID of the path to remove')
        parser.add_argument('--name', help='Name of the path to remove')
        parser.add_argument('--path', help='Path to remove')
        parser.add_argument('--csv', default='paths.csv', help='Name of the CSV file for storing paths')
        args = parser.parse_args()

        if args.id is None and args.name is None and args.path is None:
            print("Error: At least one of --id, --name, or --path must be provided.")
            return

        pm = FsoExpansion(args.csv)
        pm.remove_path(id=args.id, name=args.name, path=args.path)

    except Exception as e:
        print(f"Error in remove_path_entry function: {e}", file=sys.stderr)