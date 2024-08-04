import csv
import sys
from collections.abc import Callable
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from path_chronicle.config import Config
from path_chronicle.schema import PathEntry, check_header
from path_chronicle.utils import get_package_root


class FsoExpansion:
    """
    A class that provides extended file system operations.

    Attributes:
        package_root_dir (Path): The directory path of the package root.
        csv_dir (Path): The directory path where CSV files are stored.
        csv_file (Path): The path to the CSV file.
        paths (list): A list that stores path info.
    """

    def __init__(
        self,
        config: Config,
        csv_name: str = "paths.csv",
        csv_dir_name: str = "csv",
        csv_root_dir: str | None = None,
    ):
        """
        Constructor for the FsoExpansion class.

        Args:
            csv_name (str): The name of the CSV file. Default is "paths.csv".
            csv_dir_name (str): The name of the directory where the CSV file is stored.
                                Default is "csv".
            csv_root_dir (str | None): The root directory path for the CSV file.
                                       Default is None.
        """
        self.config = config
        self.package_root_dir = get_package_root()
        if not self.package_root_dir:
            raise FileNotFoundError("Package root directory not found.")

        self.csv_dir = (
            Path(csv_root_dir) / csv_dir_name
            if csv_root_dir
            else self.package_root_dir / csv_dir_name
        )
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.csv_file = self.csv_dir / csv_name
        self.paths = self._load_paths()

    def _load_paths(self) -> list[PathEntry]:
        """
        Loads path info from the CSV file.

        Returns:
            list[dict]: A list of path info.
        """
        paths: list[PathEntry] = []
        if not self.csv_file.exists() or self.csv_file.stat().st_size == 0:
            print("CSV file does not exist or is empty. Returning empty paths list.")
            return paths

        try:
            df = pd.read_csv(self.csv_file)
            if not check_header(list(df.columns)):
                raise ValueError("Invalid header in CSV file.")

            if df.empty:
                print("CSV file is empty. Returning empty paths list.")
                return paths

            error_paths: list[dict] = []
            idx_num = 0
            for _, row in df.iterrows():
                idx_num += 1
                try:
                    row_data = row.to_dict()
                    row_data["id"] = int(row_data["id"])
                    row_data = {
                        k: v if pd.notna(v) else None for k, v in row_data.items()
                    }
                    path_entry = PathEntry(**row_data)
                    paths.append(path_entry)

                except ValidationError as e:
                    errors = e.errors()
                    e_dict = {k: v for k, v in errors[0].items()}
                    e_dict["idx"] = idx_num
                    error_paths.append(e_dict)
                    continue

            if error_paths:
                print(
                    f"Error loading CSV rows: {error_paths}. "
                    "Please check the CSV file for errors.",
                    file=sys.stderr,
                )

        except ValueError as ve:
            print(f"Error reading CSV file in ValueError: {ve}", file=sys.stderr)
            raise

        except Exception as e:
            print(f"Error reading CSV file in Exception: {e}", file=sys.stderr)

        return paths

    def _save_paths(self) -> None:
        """
        Saves path info to the CSV file.
        """
        try:
            with open(self.csv_file, mode="w", newline="") as file:
                fieldnames = list(PathEntry.model_fields.keys())
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for path_info in self.paths:
                    writer.writerow(path_info.model_dump())

            print(f"Paths saved to CSV file at {self.csv_file}")

        except Exception as e:
            print(f"Error saving paths: {e}", file=sys.stderr)

    def _create_path_and_save_csv(
        self,
        path: Path,
        description: str,
        create_function: Callable[[Path], None],
        is_save_to_csv: bool = True,
    ) -> Path | None:
        """
        Creates a new path and optionally saves the path info to the CSV file.

        Args:
            path (str): The path to create.
            description (str): A description of the path.
            create_function (Callable): The function to create the path.
            is_save_to_csv (bool): Whether to save to the CSV file. Default is True.

        Returns:
            Path | None: The created path. None if an error occurs.
        """
        try:

            new_path = Path(path).resolve()
            name = new_path.name
            project_root = self.config.get("project_root")

            is_relative = False
            if project_root is not None and isinstance(project_root, str):
                print(f"Project root directory: {Path(project_root)}")
                new_path = new_path.relative_to(Path(project_root))
                create_path = Path(project_root) / new_path
                is_relative = True

            if not is_relative:
                create_path = new_path

            path_entry = PathEntry(
                id=max([p.id for p in self.paths], default=0) + 1,
                name=name,
                path=str(new_path),
                description=description,
            )

            create_function(create_path)
            print(f"Path created at {create_path}")

            if is_save_to_csv:
                self.paths.append(path_entry)
                self._print_csv_path()
                self._save_paths()

            return new_path

        except ValidationError as e:
            print(f"Error creating path entry: {e}", file=sys.stderr)
            return None

        except Exception as e:
            print(f"Error creating path: {e}", file=sys.stderr)
            return None

    def remove_path_and_from_csv(
        self, id: int | None = None, name: str | None = None, path: str | None = None
    ) -> None:
        """
        Removes a path based on the specified ID, name, or path,
        and also removes it from the CSV file.

        Args:
            id (int | None): The ID of the path to remove.
            name (str | None): The name of the path to remove.
            path (str | None): The string representation of the path to remove.
        """
        try:
            if not self.paths:
                print("No paths available to remove.")
                print("The CSV file is either non-existent or empty.")
                return

            target_path = self._find_target_path(id, name, path)

            if target_path:
                project_root = self.config.get("project_root")
                if project_root is not None and isinstance(project_root, str):
                    project_root_abs_path = Path(project_root)

                    if project_root_abs_path in target_path.parents:
                        target_path = target_path.relative_to(project_root_abs_path)
                        target_path = project_root_abs_path / target_path

                self._delete_path(target_path)
            else:
                print("No valid identifier provided to delete path.")

        except Exception as e:
            print(f"Error deleting path: {e}", file=sys.stderr)

    def _find_target_path(
        self, id: int | None = None, name: str | None = None, path: str | None = None
    ) -> Path | None:
        """
        Finds the target path based on the specified ID, name, or path.

        Args:
            id (int | None): The ID of the path to find.
            name (str | None): The name of the path to find.
            path (str | None): The string representation of the path to find.

        Returns:
            Path | None: The target path is absolute or relative from the project root.
        """
        target_path_str: str | None = None

        if id is not None:
            for p in self.paths:
                if p.id == id:
                    target_path_str = p.path
                    break

            if target_path_str is None:
                print(f"No path found with id: {id}")
                return None

        if name is not None and target_path_str is None:
            for p in self.paths:
                if p.name == name:
                    target_path_str = p.path
                    break

            if target_path_str is None:
                print(f"No path found with name: {name}")
                return None

        if path is not None and target_path_str is None:
            target_path_str = str(path)
            if not any(p.path == target_path_str for p in self.paths):
                print(f"No path found with path: {target_path_str}")
                return None

        if target_path_str is not None:
            target_path = Path(target_path_str)

        return target_path

    def _delete_path(self, target_path: Path) -> None:
        """
        Deletes the target path and updates the CSV file.

        Args:
            target_path (Path): The path to delete.
        """
        try:

            if target_path.exists():
                self.paths = [
                    p
                    for p in self.paths
                    if not Path(p.path).resolve().is_relative_to(target_path.resolve())
                ]

                if target_path.is_dir():
                    for item in target_path.glob("**/*"):
                        if item.is_file():
                            item.unlink()
                        else:
                            item.rmdir()
                    target_path.rmdir()
                else:
                    target_path.unlink()
                print(f"Path deleted: {target_path}")

                self._save_paths()
            else:
                print(f"Path does not exist: {target_path}")

        except Exception as e:
            print(f"Error deleting path: {e}", file=sys.stderr)

    def create_dir_and_save_csv(
        self,
        path: str,
        description: str = "",
        is_save_to_csv: bool = True,
    ) -> Path | None:
        """
        Creates a new directory and optionally saves the path info to the CSV file.

        Args:
            path (str): The path of the directory to create.
            description (str): A description of the directory.
            is_save_to_csv (bool): Whether to save to the CSV file. Default is True.

        Returns:
            Path | None: The created directory path. None if an error occurs.
        """
        return self._create_path_and_save_csv(
            Path(path),
            description,
            lambda p: p.mkdir(parents=True, exist_ok=True),
            is_save_to_csv,
        )

    def create_file_and_save_csv(
        self,
        path: str,
        description: str = "",
        is_save_to_csv: bool = True,
    ) -> Path | None:
        """
        Creates a new file and optionally saves the path info to the CSV file.

        Args:
            path (str): The path of the file to create.
            description (str): A description of the file.
            is_save_to_csv (bool): Whether to save to the CSV file. Default is True.

        Returns:
            Path | None: The created file path. None if an error occurs.
        """
        return self._create_path_and_save_csv(
            Path(path),
            description,
            lambda p: p.touch(exist_ok=True),
            is_save_to_csv,
        )

    def list_paths(self) -> None:
        """
        Lists the saved path info.
        """
        if not self.paths:
            print("No paths saved in CSV.")
        else:
            df = pd.DataFrame([p.model_dump() for p in self.paths])
            print(df.to_string(index=False))

    def _print_csv_path(self) -> None:
        """
        Prints the CSV file path info.
        """
        print(f"CSV directory: {self.csv_dir}")
        print(f"CSV file path: {self.csv_file}\n")

    def edit_csv_to_add_path(
        self,
        path: str,
        description: str | None,
    ) -> None:
        """
        Adds a new path data to the CSV file.

        Args:
            path (str): The path to add.
            description (str | None): A description of the path. Default is None.
        """
        try:
            path_obj = Path(path).resolve()
            path_entry = PathEntry(
                id=max([p.id for p in self.paths], default=0) + 1,
                name=path_obj.name,
                path=str(path_obj),
                description=description,
            )
            self.paths.append(path_entry)
            self._save_paths()
            print(f"Path added: {path_entry}")
        except Exception as e:
            print(f"Error adding path entry: {e}", file=sys.stderr)

    def edit_csv_to_remove_path(
        self,
        id: int | None = None,
        name: str | None = None,
        path: str | None = None,
    ) -> None:
        """
        Removes a path data from the CSV file.

        Args:
            id (int): The ID of the path entry to remove.
            name (str): The name of the path entry to remove.
            path (str): The path of the path entry to remove.
        """
        try:

            if id and [p for p in self.paths if p.id == id]:
                self.paths = [p for p in self.paths if p.id != id]

            elif name and [p for p in self.paths if p.name == name]:
                self.paths = [p for p in self.paths if p.name != name]

            elif path and [p for p in self.paths if p.path == path]:
                self.paths = [p for p in self.paths if p.path != path]

            else:
                raise ValueError("No valid identifier provided to remove path.")

            self._save_paths()
            print(f"Path removed: {id or name or path}")
        except Exception as e:
            print(f"Error removing path entry: {e}", file=sys.stderr)
