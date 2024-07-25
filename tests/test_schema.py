import pytest
from pydantic import ValidationError

from path_chronicle.schema import PathEntry, check_header


def test_id_must_be_positive():
    with pytest.raises(ValidationError) as exc_info:
        PathEntry(
            id=-1,
            name="valid_name",
            path="/valid/path",
            description="valid description",
        )
    assert "id must be positive" in str(exc_info.value)


def test_name_must_not_be_empty():
    with pytest.raises(ValidationError) as exc_info:
        PathEntry(id=1, name="", path="/valid/path", description="valid description")
    assert "name must not be empty" in str(exc_info.value)


def test_name_must_not_contain_invalid_chars():
    invalid_names = ["invalid name", "invalid$name", "invalid@name", "invalid#name"]
    for name in invalid_names:
        with pytest.raises(ValidationError) as exc_info:
            PathEntry(
                id=1, name=name, path="/valid/path", description="valid description"
            )
        assert "name must not contain invalid chars" in str(exc_info.value)


def test_name_must_not_be_a_path():
    with pytest.raises(ValidationError) as exc_info:
        PathEntry(
            id=1, name="valid/name", path="/valid/path", description="valid description"
        )
    assert "name is file or directory name, not a path" in str(exc_info.value)


def test_path_must_not_be_empty():
    with pytest.raises(ValidationError) as exc_info:
        PathEntry(id=1, name="valid_name", path="", description="valid description")
    assert "path must not be empty" in str(exc_info.value)


def test_valid_path_entry():
    entry = PathEntry(
        id=1, name="valid_name", path="/valid/path", description="valid description"
    )
    assert entry.id == 1
    assert entry.name == "valid_name"
    assert entry.path == "/valid/path"
    assert entry.description == "valid description"


def test_check_header_valid(setup_test_dir_paths):
    header = list(setup_test_dir_paths[0].keys())
    assert check_header(header)


def test_check_header_invalid_order(setup_test_dir_paths):
    header = list(setup_test_dir_paths[0].keys())
    header = header[1:] + header[:1]
    assert not check_header(header)


def test_check_header_invalid_headers(setup_test_dir_paths):
    header = list(setup_test_dir_paths[0].keys())
    header[3] = "desc"
    assert not check_header(header)
