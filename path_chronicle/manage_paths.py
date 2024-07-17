import csv
from pathlib import Path
import argparse
import sys

class PathManager:
    def __init__(self, csv_file):
        self.script_dir = Path(__file__).parent  # スクリプトが存在するディレクトリ
        print(f"Script directory: {self.script_dir}")  # デバッグ出力
        self.csv_dir = self.script_dir / 'csv'
        self.csv_dir.mkdir(exist_ok=True)  # 'csv'ディレクトリを作成
        print(f"CSV directory: {self.csv_dir}")  # デバッグ出力
        self.csv_file = self.csv_dir / csv_file
        print(f"CSV file path: {self.csv_file}")  # デバッグ出力
        self.paths = self.load_paths()  # self.pathsの初期化

    def load_paths(self):
        paths = {}
        if not self.csv_file.exists():
            print(f"CSV file does not exist. Creating new CSV file at {self.csv_file}")  # デバッグ出力
            self.paths = paths
            self.save_paths()  # CSVファイルが存在しない場合、新規に作成
        else:
            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    paths[row['name']] = row['path']
            self.paths = paths
        return paths

    def save_paths(self):
        try:
            with open(self.csv_file, mode='w', newline='') as file:
                fieldnames = ['name', 'path']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for name, path in self.paths.items():
                    writer.writerow({'name': name, 'path': path})
            print(f"Paths saved to CSV file at {self.csv_file}")  # デバッグ出力
        except Exception as e:
            print(f"Error saving paths: {e}", file=sys.stderr)

    def create_dir(self, name, parent_dir, save_to_csv=True):
        try:
            parent_path = Path(parent_dir)
            new_dir = parent_path / name
            new_dir.mkdir(parents=True, exist_ok=True)
            print(f"Directory created at {new_dir}")  # デバッグ出力
            if save_to_csv:
                self.paths[name] = str(new_dir)
                self.save_paths()
            return new_dir
        except Exception as e:
            print(f"Error creating directory: {e}", file=sys.stderr)

    def create_file(self, name, parent_dir, save_to_csv=True):
        try:
            parent_path = Path(parent_dir)
            new_file = parent_path / name
            new_file.touch(exist_ok=True)  # Create the file if it doesn't exist
            print(f"File created at {new_file}")  # デバッグ出力
            if save_to_csv:
                self.paths[name] = str(new_file)
                self.save_paths()
            return new_file
        except Exception as e:
            print(f"Error creating file: {e}", file=sys.stderr)

def main():
    try:
        parser = argparse.ArgumentParser(description='Manage project paths and files.')
        parser.add_argument('action', choices=['create_dir', 'create_file'], help='Action to perform')
        parser.add_argument('name', help='Name of the directory or file to create')
        parser.add_argument('parent_dir', help='Parent directory where the directory or file will be created')
        parser.add_argument('--csv', default='paths.csv', help='Name of the CSV file for storing paths')
        parser.add_argument('--no-save', action='store_true', help='Do not save the path to the CSV file')

        args = parser.parse_args()

        pm = PathManager(args.csv)
        save_to_csv = not args.no_save

        if args.action == 'create_dir':
            pm.create_dir(args.name, args.parent_dir, save_to_csv)
        elif args.action == 'create_file':
            pm.create_file(args.name, args.parent_dir, save_to_csv)
    except Exception as e:
        print(f"Error in main function: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
