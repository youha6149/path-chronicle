import csv
import sys
from collections.abc import Callable
from pathlib import Path

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
        self.package_root_dir = get_package_root()
        self.csv_dir = (
            Path(csv_root_dir) / csv_dir_name
            if csv_root_dir
            else self.package_root_dir / csv_dir_name
        )
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.csv_file = self.csv_dir / csv_name
        self.paths = self._load_paths()

    def _load_paths(self) -> list[dict]:
        """
        Loads path info from the CSV file.

        Returns:
            list[dict]: A list of path info.
        """
        paths: list = []
        if not self.csv_file.exists() or self.csv_file.stat().st_size == 0:
            print("CSV file does not exist or is empty. Returning empty paths list.")
            return paths

        try:
            with open(self.csv_file, mode="r") as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                if not rows:
                    if not check_header(list(reader.fieldnames or [])):
                        raise ValueError("Invalid header in CSV file.")

                    print("CSV file only contains headers. Returning empty paths list.")
                    return paths
                for row in rows:
                    path_entry = PathEntry(
                        id=int(row["id"]),
                        name=row["name"],
                        path=row["path"],
                        description=row["description"],
                    )
                    paths.append(path_entry.model_dump())

        except Exception as e:
            print(f"Error reading CSV file: {e}", file=sys.stderr)

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
                    writer.writerow(path_info)

            print(f"Paths saved to CSV file at {self.csv_file}")

        except Exception as e:
            print(f"Error saving paths: {e}", file=sys.stderr)

    def _create_path_and_save_csv(
        self,
        name: str,
        parent_dir: str,
        description: str,
        create_function: Callable[[Path], None],
        is_save_to_csv: bool = True,
    ) -> Path | None:
        """
        Creates a new path and optionally saves the path info to the CSV file.

        Args:
            name (str): The name of the path to create.
            parent_dir (str): The path of the parent directory.
            description (str): A description of the path.
            create_function (Callable[[Path], None]): A function to create the path.
            is_save_to_csv (bool): Whether to save to the CSV file. Default is True.

        Returns:
            Path | None: The created path object. None if an error occurs.
        """
        try:
            parent_path = Path(parent_dir)
            new_path = parent_path / name
            create_function(new_path)
            print(f"Path created at {new_path}")

            if is_save_to_csv:
                self._print_csv_path()

                path_entry = PathEntry(
                    id=max([p["id"] for p in self.paths], default=0) + 1,
                    name=name.replace(".", "_"),
                    path=str(new_path),
                    description=description,
                )

                self.paths.append(path_entry.model_dump())
                self._save_paths()

            return new_path

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

            target_path = None

            if id is not None:
                for p in self.paths:
                    if p["id"] == id:
                        target_path = p["path"]
                        break

                if target_path is None:
                    print(f"No path found with id: {id}")
                    return

            if name is not None and target_path is None:
                for p in self.paths:
                    if p["name"] == name:
                        target_path = p["path"]
                        break

                if target_path is None:
                    print(f"No path found with name: {name}")
                    return

            if path is not None and target_path is None:
                target_path = str(path)
                if not any(p["path"] == target_path for p in self.paths):
                    print(f"No path found with path: {target_path}")
                    return

            if target_path:
                path_obj = Path(target_path)
                if path_obj.exists():
                    self.paths = [
                        p
                        for p in self.paths
                        if not Path(p["path"])
                        .resolve()
                        .is_relative_to(path_obj.resolve())
                    ]

                    if path_obj.is_dir():
                        for item in path_obj.glob("**/*"):
                            if item.is_file():
                                item.unlink()
                            else:
                                item.rmdir()
                        path_obj.rmdir()
                    else:
                        path_obj.unlink()
                    print(f"Path deleted: {target_path}")

                    self._save_paths()
                else:
                    print(f"Path does not exist: {target_path}")
            else:
                print("No valid identifier provided to delete path.")

        except Exception as e:
            print(f"Error deleting path: {e}", file=sys.stderr)

    def create_dir_and_save_csv(
        self,
        name: str,
        parent_dir: str,
        description: str = "",
        is_save_to_csv: bool = True,
    ) -> Path | None:
        """
        Creates a new directory and optionally saves the path info to the CSV file.

        Args:
            name (str): The name of the directory to create.
            parent_dir (str): The path of the parent directory.
            description (str): A description of the directory.
            is_save_to_csv (bool): Whether to save to the CSV file. Default is True.

        Returns:
            Path | None: The created directory path. None if an error occurs.
        """
        return self._create_path_and_save_csv(
            name,
            parent_dir,
            description,
            lambda p: p.mkdir(parents=True, exist_ok=True),
            is_save_to_csv,
        )

    def create_file_and_save_csv(
        self,
        name: str,
        parent_dir: str,
        description: str = "",
        is_save_to_csv: bool = True,
    ) -> Path | None:
        """
        Creates a new file and optionally saves the path info to the CSV file.

        Args:
            name (str): The name of the file to create.
            parent_dir (str): The path of the parent directory.
            description (str): A description of the file.
            is_save_to_csv (bool): Whether to save to the CSV file. Default is True.

        Returns:
            Path | None: The created file path. None if an error occurs.
        """
        return self._create_path_and_save_csv(
            name,
            parent_dir,
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
            self._print_table(
                list(PathEntry.model_fields.keys()),
                [
                    (str(p["id"]), p["name"], p["path"], p["description"])
                    for p in self.paths
                ],
            )

    def _print_csv_path(self) -> None:
        """
        Prints the CSV file path info.
        """
        print(f"CSV directory: {self.csv_dir}")
        print(f"CSV file path: {self.csv_file}\n")

    def _print_table(self, headers, rows) -> None:
        """
        Displays data in a table format.

        Args:
            headers (list): The table headers.
            rows (list): The table row data.
        """
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        header_row = " | ".join(
            f"{header:{col_widths[i]}}" for i, header in enumerate(headers)
        )
        print(header_row)
        print("-+-".join("-" * width for width in col_widths))

        for row in rows:
            print(" | ".join(f"{cell:{col_widths[i]}}" for i, cell in enumerate(row)))

        print()
