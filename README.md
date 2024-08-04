# How to Use Path Chronicle CLI

This guide provides instructions on how to use the Path Chronicle command-line interface (CLI) for managing paths in your project. Below are the available commands and how to use them.

## Where to get it

```
pip install path-chronicle
```

## Commands

    
1. [Set Project Root Directory](#set-project-root-directory)
2. [Create a Directory and Save to CSV](#create-a-directory-and-save-to-csv)
3. [Create a File and Save to CSV](#create-a-file-and-save-to-csv)
4. [List All Paths in CSV](#list-all-paths-in-csv)
5. [Remove a Path from CSV](#remove-a-path-from-csv)
6. [Generate Paths Python File](#generate-paths-python-file)
7. [Add a Path to CSV](#add-a-path-to-csv)
8. [Remove a Path from CSV by Criteria](#remove-a-path-from-csv-by-criteria)

## Set Project Root Directory
※Recommended to run immediately after installation

Sets the project root directory in the config file.

### Example Usage

```bash
pcsetpjroot ./
pcsetpjroot /path/to/project
```

## Create a Directory and Save to CSV

Creates a directory and optionally saves the path info to the CSV file.

### Example Usage

```bash
pcmkdir ./my_temp_directory --description "Temporary directory for storage"
```

## Create a File and Save to CSV

Creates a file and optionally saves the path info to the CSV file.

### Example Usage

```bash
pctouch ./my_temp_directory/another_file.txt --description "Another file for testing"
```

## List All Paths in CSV

Lists all paths stored in the CSV file.

### Example Usage

```bash
pcpathslist
```

## Remove a Path from CSV

Removes a path based on ID, name, or path, and also removes it from the CSV file.

### Example Usage

```bash
pcrmpath --id 1
pcrmpath --name example_name
pcrmpath --path /example/path/to/delete
```

## Generate Paths Python File

Generates a Python file with paths for project directories and files.

### Example Usage

```bash
gpaths
gpaths --csv_root_dir ./csv --module_root_dir ./path_module --module_name paths.py
```

### Example of Module Created

```path_archives.py
from pathlib import Path


class PathArchives:
    """
    This class provides paths for various project directories and files.
    """

    my_temp_directory = Path('my_temp_directory')
    another_file_txt = Path('my_temp_directory/another_file.txt')

    @staticmethod
    def get_path(name: str) -> Path:
        """
        Returns the Path object for the given name.

        Available paths:
        - my_temp_directory: my_temp_directory
        - another_file_txt: my_temp_directory/another_file.txt
        """
        return getattr(PathArchives, name, None) or Path("")

```

## Add a Path to CSV

Adds a path to the CSV file.

### Example Usage

```bash
pcaddtocsv ./my_temp_directory --description "Temporary directory for storage"
```

## Remove a Path from CSV by Criteria

Removes a path from the CSV file based on ID, name, or path.

### Example Usage

```bash
pcrmtocsv --id 1
pcrmtocsv --name example_name
pcrmtocsv --path /example/path/to/delete
```

## Common Arguments

- `path`: The path to the directory or file.
- `--description`: A description for the directory or file.
- `--csv_name`: Name of the CSV file for storing paths. Default is "paths.csv".
- `--csv_root_dir`: Root directory where the CSV file will be stored.
- `--csv_dir_name`: Name of the directory containing the CSV file. Default is "csv".
- `--no-save`: Do not save the path to the CSV file.
- `--config_root_dir`: Root directory where the config file is located.

This guide provides a comprehensive overview of the commands available in the Path Chronicle CLI for managing paths in your project. Each command includes example usage and the corresponding function definition.
