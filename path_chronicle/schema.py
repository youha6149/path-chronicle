import sys

from pydantic import BaseModel, field_validator


class PathEntry(BaseModel):
    """
    Represents an entry in the path chronicle.

    Attributes:
        id (int): The unique identifier for the path entry.
        name (str): The name of file or directory associated with the entry.
        path (str): The path of from the root directory to the file or directory,
                    or absolute path.
        description (str, optional): The description of the path entry.
    """

    id: int
    name: str
    path: str
    description: str | None

    @field_validator("id")
    def id_must_be_positive(cls, v):
        """
        Validates that the given ID is a positive integer.

        Args:
            v (int): The ID to be validated.

        Raises:
            ValueError: If the ID is not a positive integer.

        Returns:
            int: The validated ID.

        """
        if v < 0:
            raise ValueError("id must be positive")
        return v

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        """
        Validates that the name is not empty.

        Args:
            v (str): The name to be validated.

        Raises:
            ValueError: If the name is empty.

        Returns:
            str: The validated name.
        """
        if not v:
            raise ValueError("name must not be empty")
        return v

    @field_validator("name")
    def name_must_not_contain_invalid_chars(cls, v):
        """
        Validates that the given name does not contain any invalid characters.

        Args:
            v (str): The name to be validated.

        Raises:
            ValueError: If the name contains any invalid characters or if it is a path.

        Returns:
            str: The validated name.

        """
        path_sep = "/"
        invalid_chars = set(" !@#$%^&*()-+=[]{}|\\:;'\",<>?`~")

        if any(char in invalid_chars for char in v):
            raise ValueError(f"name must not contain invalid chars: {invalid_chars}")

        if path_sep in v:
            raise ValueError("name is file or directory name, not a path")
        return v

    @field_validator("path")
    def path_must_not_be_empty(cls, v):
        """
        Validates that the path is not empty.

        Args:
            v (str): The path to be validated.

        Raises:
            ValueError: If the path is empty.

        Returns:
            str: The validated path.
        """
        if not v:
            raise ValueError("path must not be empty")
        return v


def check_header(header: list[str]) -> bool:
    """
    Check if the header of the CSV file is valid.

    Args:
        header: The header of the CSV file.

    Returns:
        bool: True if the header is valid, False otherwise.
    """
    expected_header = list(PathEntry.model_fields.keys())
    if header != expected_header:
        if set(header) != set(expected_header):
            e = (
                f"Invalid header in CSV file. "
                f"Expected headers: {expected_header}, "
                f"but got: {header}"
            )
            print(e, file=sys.stderr)
            return False
        else:
            e = (
                f"Header order is incorrect. "
                f"Expected order: {expected_header}, "
                f"but got: {header}"
            )
            print(e, file=sys.stderr)
            return False
    return True


def normalize_name(name: str) -> str:
    """
    Normalize the name by replacing dots with underscores, except the leading dot.

    Args:
        name (str): The original name.

    Returns:
        str: The normalized name.
    """
    if name.startswith("."):
        return "." + name[1:].replace(".", "_")
    return name.replace(".", "_")
