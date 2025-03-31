import shutil
import hashlib
import logging
import pytest
from sync import compare_and_sync_folders, calculate_file_hash


@pytest.fixture
def log_checker(caplog):
    """
    A reusable log assertion helper for testing functions that generate log messages.

    This fixture captures log output and checks if the expected log messages appear
    *only after* the function execution, preventing false positives from earlier logs.

    Args:
        func (callable): The function to execute.
        expected_messages (str): The log message or substring expected in the logs.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Raises:
        AssertionError: If the expected log message is not found after execution.
    """

    def _check_logs(func, expected_messages, *args, **kwargs):
        with caplog.at_level(logging.INFO):
            before_count = len(caplog.records)
            assert expected_messages not in caplog.text
            func(*args, **kwargs)  # Call function with arguments

            logs_after_execution = caplog.records[before_count:]
            messages_after_execution = [record.message for record in logs_after_execution]

        assert any(expected_messages in message for message in messages_after_execution), "Expected log not found"

    return _check_logs


@pytest.fixture
def setup_test_folders(tmp_path):
    """
    Creates temporary source and replica directories with test files.
    """
    source = tmp_path / "source"
    replica = tmp_path / "replica"

    source.mkdir()
    replica.mkdir()

    # Create sample files
    (source / "file1.txt").write_text("Hello World")
    (source / "file2.txt").write_text("Python Testing")

    # Create a subfolder with a file
    (source / "subfolder").mkdir()
    (source / "empty_subfolder").mkdir()
    (source / "subfolder/file3.txt").write_text("Inside folder")

    yield source, replica

    # Cleanup after test
    shutil.rmtree(source)
    shutil.rmtree(replica)


def test_file_hashing(setup_test_folders):
    """Test that file hashing works correctly."""
    source, _ = setup_test_folders
    file_path = source / "file1.txt"

    expected_hash = hashlib.sha256("Hello World".encode()).hexdigest()
    assert calculate_file_hash(file_path) == expected_hash


def test_sync_creates_missing_files(setup_test_folders):
    """Test that missing files are copied from source to replica."""
    source, replica = setup_test_folders

    compare_and_sync_folders(source, replica, "test.log")

    assert (replica / "file1.txt").exists()
    assert (replica / "file2.txt").exists()
    assert (replica / "subfolder/file3.txt").exists()
    assert (source / "empty_subfolder").exists()


def test_sync_updates_modified_files(setup_test_folders, log_checker, caplog):
    """Test that modified files in source overwrite replica files."""
    source, replica = setup_test_folders
    expected_message = "Updated file (content changed):"
    (replica / "file1.txt").write_text("OLD CONTENT")

    log_checker(compare_and_sync_folders, expected_message, source, replica, "test.log")
    assert (replica / "file1.txt").read_text() == "Hello World"


def test_sync_removes_extra_files(setup_test_folders, log_checker, caplog):
    """Test that extra files in replica (not in source) are deleted."""
    source, replica = setup_test_folders
    extra_file = replica / "extra.txt"
    extra_file.write_text("I should be deleted!")

    log_checker(compare_and_sync_folders, "Removed file:", source, replica, "test.log")
    assert not extra_file.exists()


def test_sync_creates_missing_folders(setup_test_folders, log_checker, caplog):
    """Test that missing files are copied from source subdirectories to replica."""
    source, replica = setup_test_folders
    expected_message = "Copied new directory:"

    log_checker(compare_and_sync_folders, expected_message, source, replica, "test.log")
    assert (source / "empty_subfolder").exists()


def test_logging_output(setup_test_folders, log_checker, caplog):
    """Test that logging records synchronization events."""
    source, replica = setup_test_folders
    expected_message = "Copied file:"

    log_checker(compare_and_sync_folders, expected_message, source, replica, "test.log")
