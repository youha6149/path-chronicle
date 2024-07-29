## How to Use Path Chronicle CLI

This guide provides instructions on how to use the Path Chronicle command-line interface (CLI) for managing paths in your project. Below are the available commands and how to use them.

### Commands

1. [Create a Directory and Save to CSV](#create-a-directory-and-save-to-csv)
2. [Create a File and Save to CSV](#create-a-file-and-save-to-csv)
3. [List All Paths in CSV](#list-all-paths-in-csv)
4. [Remove a Path from CSV](#remove-a-path-from-csv)
5. [Generate Paths Python File](#generate-paths-python-file)
6. [Set Project Root Directory](#set-project-root-directory)
7. [Add a Path to CSV](#add-a-path-to-csv)
8. [Remove a Path from CSV by Criteria](#remove-a-path-from-csv-by-criteria)

### Create a Directory and Save to CSV

Creates a directory and optionally saves the path info to the CSV file.

#### Example Usage

```bash
poetry run pcmkdir ./my_temp_directory --description "Temporary directory for storage"
```

#### Function Definition

```python
def create_dir_and_save_csv_entry():
    # Implementation
```

### Create a File and Save to CSV

Creates a file and optionally saves the path info to the CSV file.

#### Example Usage

```bash
poetry run pctouch ./my_temp_directory/another_file.txt --description "Another file for testing"
```

#### Function Definition

```python
def create_file_and_save_csv_entry():
    # Implementation
```

### List All Paths in CSV

Lists all paths stored in the CSV file.

#### Example Usage

```bash
poetry run pcpathslist
```

#### Function Definition

```python
def list_paths_entry():
    # Implementation
```

### Remove a Path from CSV

Removes a path based on ID, name, or path, and also removes it from the CSV file.

#### Example Usage

```bash
poetry run pcrmpath --id 1
poetry run pcrmpath --name example_name
poetry run pcrmpath --path /example/path/to/delete
```

#### Function Definition

```python
def remove_path_and_from_csv_entry():
    # Implementation
```

### Generate Paths Python File

Generates a Python file with paths for project directories and files.

#### Example Usage

```bash
poetry run gpaths
poetry run gpaths --csv_root_dir ./csv --module_root_dir ./path_module --module_name paths.py
```

#### Function Definition

```python
def generate_paths_entry():
    # Implementation
```

### Set Project Root Directory

Sets the project root directory in the config file.

#### Example Usage

```bash
poetry run pcsetpjroot ./
poetry run pcsetpjroot /path/to/project
```

#### Function Definition

```python
def set_project_root_entry():
    # Implementation
```

### Add a Path to CSV

Adds a path to the CSV file.

#### Example Usage

```bash
poetry run pcaddtocsv ./my_temp_directory --description "Temporary directory for storage"
```

#### Function Definition

```python
def edit_csv_to_add_path_entry():
    # Implementation
```

### Remove a Path from CSV by Criteria

Removes a path from the CSV file based on ID, name, or path.

#### Example Usage

```bash
poetry run pcrmtocsv --id 1
poetry run pcrmtocsv --name example_name
poetry run pcrmtocsv --path /example/path/to/delete
```

#### Function Definition

```python
def edit_csv_to_remove_path_entry():
    # Implementation
```

### Common Arguments

- `path`: The path to the directory or file.
- `--description`: A description for the directory or file.
- `--csv_name`: Name of the CSV file for storing paths. Default is "paths.csv".
- `--csv_root_dir`: Root directory where the CSV file will be stored.
- `--csv_dir_name`: Name of the directory containing the CSV file. Default is "csv".
- `--no-save`: Do not save the path to the CSV file.
- `--config_root_dir`: Root directory where the config file is located.

This guide provides a comprehensive overview of the commands available in the Path Chronicle CLI for managing paths in your project. Each command includes example usage and the corresponding function definition.