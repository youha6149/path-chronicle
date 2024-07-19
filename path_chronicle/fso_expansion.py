import argparse
import csv
from collections.abc import Callable
from pathlib import Path
import sys

class FsoExpansion:
    def __init__(self, csv_file: str):
        self.script_dir = Path(__file__).parent
        self.csv_dir = self.script_dir / 'csv'
        self.csv_dir.mkdir(exist_ok=True)
        self.csv_file = self.csv_dir / csv_file
        self.paths = self._load_paths()

    def _load_paths(self) -> list[dict]:
        paths = []
        if not self.csv_file.exists() or self.csv_file.stat().st_size == 0:
            print(f"CSV file does not exist or is empty. Returning empty paths list.")
            return paths

        try:
            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    paths.append({'id': int(row['id']), 'name': row['name'], 'path': row['path'], 'description': row['description']})

        except Exception as e:
            print(f"Error reading CSV file: {e}", file=sys.stderr)

        return paths

    def _save_paths(self) -> None:
        try:
            with open(self.csv_file, mode='w', newline='') as file:
                fieldnames = ['id', 'name', 'path', 'description']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for path_info in self.paths:
                    writer.writerow(path_info)

            print(f"Paths saved to CSV file at {self.csv_file}")

        except Exception as e:
            print(f"Error saving paths: {e}", file=sys.stderr)

    def _create_path(self, name: str, parent_dir: str, description: str, create_function: Callable[[Path], None], is_save_to_csv: bool=True) -> Path:
        try:
            parent_path = Path(parent_dir)
            new_path = parent_path / name
            create_function(new_path)
            print(f"Path created at {new_path}")

            if is_save_to_csv:
                self._print_csv_path()
                new_id = max([p['id'] for p in self.paths], default=0) + 1
                self.paths.append({'id': new_id, 'name': name, 'path': str(new_path), 'description': description})
                self._save_paths()

            return new_path

        except Exception as e:
            print(f"Error creating path: {e}", file=sys.stderr)

    def remove_path(self, id: int = None, name: str = None, path: str = None) -> None:
        try:
            target_path = None

            if id is not None:
                for p in self.paths:
                    if p['id'] == id:
                        target_path = p['path']
                        break
                
                if target_path is None:
                    print(f"No path found with id: {id}")
                    return

            if name is not None and target_path is None:
                for p in self.paths:
                    if p['name'] == name:
                        target_path = p['path']
                        break
                
                if target_path is None:
                    print(f"No path found with name: {name}")
                    return

            if path is not None and target_path is None:
                target_path = path
                if not any(p['path'] == path for p in self.paths):
                    print(f"No path found with path: {path}")
                    return

            if target_path:
                path_obj = Path(target_path)
                if path_obj.exists():
                    if path_obj.is_dir():
                        for item in path_obj.glob('**/*'):
                            if item.is_file():
                                item.unlink()
                            else:
                                item.rmdir()
                        path_obj.rmdir()
                    else:
                        path_obj.unlink()
                    print(f"Path deleted: {target_path}")

                    self.paths = [p for p in self.paths if p['path'] != target_path]
                    self._save_paths()
                else:
                    print(f"Path does not exist: {target_path}")
            else:
                print("No valid identifier provided to delete path.")

        except Exception as e:
            print(f"Error deleting path: {e}", file=sys.stderr)

    def create_dir(self, name: str, parent_dir: str, description: str = '', is_save_to_csv: bool=True) -> Path:
        return self._create_path(name, parent_dir, description, lambda p: p.mkdir(parents=True, exist_ok=True), is_save_to_csv)

    def create_file(self, name: str, parent_dir: str, description: str = '', is_save_to_csv: bool=True) -> Path:
        return self._create_path(name, parent_dir, description, lambda p: p.touch(exist_ok=True), is_save_to_csv)
    
    def list_paths(self) -> None:
        if not self.paths:
            print("No paths saved in CSV.")
        else:
            self._print_table(["ID", "Name", "Path", "Description"], 
                              [(str(p['id']), p['name'], p['path'], p['description']) for p in self.paths])

    def _print_csv_path(self) -> None:
        print(f"CSV directory: {self.csv_dir}")
        print(f"CSV file path: {self.csv_file}\n")

    def _print_table(self, headers, rows) -> None:
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        header_row = " | ".join(f"{header:{col_widths[i]}}" for i, header in enumerate(headers))
        print(header_row)
        print("-+-".join('-' * width for width in col_widths))

        for row in rows:
            print(" | ".join(f"{cell:{col_widths[i]}}" for i, cell in enumerate(row)))
        
        print()

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