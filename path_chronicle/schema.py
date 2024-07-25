import sys

from pydantic import BaseModel, field_validator


class PathEntry(BaseModel):
    id: int
    name: str
    path: str
    description: str | None

    @field_validator("id")
    def id_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("id must be positive")
        return v

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("name must not be empty")
        return v

    @field_validator("name")
    def name_must_not_contain_invalid_chars(cls, v):
        path_sep = "/"
        invalid_chars = set(" !@#$%^&*()-+=[]{}|\\:;'\",.<>?`~")

        if any(char in invalid_chars for char in v):
            raise ValueError(f"name must not contain invalid chars: {invalid_chars}")

        if path_sep in v:
            raise ValueError("name is file or directory name, not a path")
        return v

    @field_validator("path")
    def path_must_not_be_empty(cls, v):
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
