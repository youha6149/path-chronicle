import csv
from pathlib import Path
import argparse

def generate_paths(csv_file="paths.csv", output_file="paths.py"):
    """インテリセンスを表示することのできるパス管理関数"""
    
    with open(Path(__file__).parent / csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        paths = {row['name']: row['path'] for row in reader}
    
    lines = [
        "from pathlib import Path\n",
        "\n",
        "class Paths:\n",
        "    \"\"\"\n",
        "    This class provides paths for various project directories and files.\n",
    ]

    lines.append("    \"\"\"\n\n")

    for name, path in paths.items():
        lines.append(f"    {name} = Path('{path}')\n")
    
    lines.append("\n    @staticmethod\n")
    lines.append("    def get_path(name: str) -> Path:\n")
    lines.append("        \"\"\"\n")
    lines.append("        Returns the Path object for the given name.\n\n")
    lines.append("        Available paths:\n")
    
    for name, path in paths.items():
        lines.append(f"        - {name}: {path}\n")

    lines.append("        \"\"\"\n")
    lines.append("        return getattr(Paths, name, None)\n")
    
    with open(output_file, mode='w') as file:
        file.writelines(lines)

def main():
    parser = argparse.ArgumentParser(description='Generate a Python file with paths for various project directories and files.')
    parser.add_argument('--csv', default='paths.csv', help='Path to the CSV file containing paths')
    parser.add_argument('--output', default='paths.py', help='Path to the output Python file')

    args = parser.parse_args()

    generate_paths(csv_file=args.csv, output_file=args.output)

if __name__ == "__main__":
    main()