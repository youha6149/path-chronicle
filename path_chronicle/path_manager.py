import csv
from pathlib import Path
import argparse
import sys
from collections.abc import Callable

class PathManager:
    def __init__(self, csv_file: str):
        self.script_dir = Path(__file__).parent
        print(f"Script directory: {self.script_dir}")

        self.csv_dir = self.script_dir / 'csv'
        self.csv_dir.mkdir(exist_ok=True)
        print(f"CSV directory: {self.csv_dir}")

        self.csv_file = self.csv_dir / csv_file
        print(f"CSV file path: {self.csv_file}")
        
        self.paths = self._load_paths()

    def _load_paths(self) -> dict[str, str]:
        paths = {}
        if not self.csv_file.exists() or self.csv_file.stat().st_size == 0:
            print(f"CSV file does not exist or is empty. Returning empty paths dictionary.")
            return paths
        
        try:
            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    paths[row['name']] = row['path']

        except Exception as e:
            print(f"Error reading CSV file: {e}", file=sys.stderr)

        return paths

    def _save_paths(self) -> None:
        try:
            with open(self.csv_file, mode='w', newline='') as file:
                fieldnames = ['name', 'path']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for name, path in self.paths.items():
                    writer.writerow({'name': name, 'path': path})

            print(f"Paths saved to CSV file at {self.csv_file}")

        except Exception as e:
            print(f"Error saving paths: {e}", file=sys.stderr)

    def _create_path(self, name: str, parent_dir: str, create_function: Callable[[Path], None], is_save_to_csv: bool=True) -> Path:
        try:
            parent_path = Path(parent_dir)
            new_path = parent_path / name
            create_function(new_path)
            print(f"Path created at {new_path}")

            if is_save_to_csv:
                self.paths[name] = str(new_path)
                self._save_paths()

            return new_path
        
        except Exception as e:
            print(f"Error creating path: {e}", file=sys.stderr)

    def create_dir(self, name: str, parent_dir: str, is_save_to_csv: bool=True) -> Path:
        return self._create_path(name, parent_dir, lambda p: p.mkdir(parents=True, exist_ok=True), is_save_to_csv)

    def create_file(self, name: str, parent_dir: str, is_save_to_csv: bool=True) -> Path:
        return self._create_path(name, parent_dir, lambda p: p.touch(exist_ok=True), is_save_to_csv)
    
def _common_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('name', help='Name of the directory or file to create')
    parser.add_argument('parent_dir', help='Parent directory where the directory or file will be created')
    parser.add_argument('--csv', default='paths.csv', help='Name of the CSV file for storing paths')
    parser.add_argument('--no-save', action='store_true', help='Do not save the path to the CSV file')
    return parser

def create_dir_entry():
    """
    ex:
        poetry run pcmkdir my_temp_directory ./
    """
    
    try:
        parser = _common_parser('Create a directory.')
        args = parser.parse_args()

        pm = PathManager(args.csv)
        is_save_to_csv = not args.no_save
        pm.create_dir(args.name, args.parent_dir, is_save_to_csv)

    except Exception as e:
        print(f"Error in create_dir_entry function: {e}", file=sys.stderr)

def create_file_entry():
    """
    ex:
        poetry run pctouch another_file.txt my_temp_directory
    """

    try:
        parser = _common_parser('Create a file.')
        args = parser.parse_args()

        pm = PathManager(args.csv)
        is_save_to_csv = not args.no_save
        pm.create_file(args.name, args.parent_dir, is_save_to_csv)

    except Exception as e:
        print(f"Error in create_file_entry function: {e}", file=sys.stderr)
