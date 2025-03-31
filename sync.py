import os
import hashlib
import shutil
import time
import argparse
import logging
from filecmp import dircmp
from pathlib import Path


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculate the hash of a file using the specified hashing algorithm (default: SHA-256).
    """
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def compare_and_sync_folders(source: str, replica: str, log_file: str) -> None:
    """
    Compare and synchronize two folders, logging actions to the log file.
    """
    source = Path(source)
    replica = Path(replica)
    comparison = dircmp(source, replica)

    compare_and_update_files(comparison, source, replica)
    copy_new_or_modified_files(comparison, source, replica)
    remove_extra_files_or_dirs(comparison, replica)

    # Recursively sync subdirectories
    for sub_dir in comparison.common_dirs:
        compare_and_sync_folders(
            os.path.join(source, sub_dir), os.path.join(replica, sub_dir), log_file
        )


def compare_and_update_files(comparison: dircmp, source: Path, replica: Path) -> None:
    """
    Compare and update files based on hash values.
    """
    for file_name in comparison.common_files:
        source_path = os.path.join(source, file_name)
        replica_path = os.path.join(replica, file_name)

        if calculate_file_hash(source_path) != calculate_file_hash(replica_path):
            shutil.copy2(source_path, replica_path)
            logging.info(
                f"Updated file (content changed): {source_path} -> {replica_path}"
            )


def copy_new_or_modified_files(comparison: dircmp, source: Path, replica: Path) -> None:
    """
    Copy new or modified files or directories from source to replica.
    """
    for file_name in comparison.left_only + comparison.diff_files:
        source_path = os.path.join(source, file_name)
        replica_path = os.path.join(replica, file_name)

        if os.path.isdir(source_path):
            shutil.copytree(source_path, replica_path)
            logging.info(f"Copied new directory: {source_path} -> {replica_path}")
        else:
            shutil.copy2(source_path, replica_path)
            logging.info(f"Copied file: {source_path} -> {replica_path}")


def remove_extra_files_or_dirs(comparison: dircmp, replica: Path) -> None:
    """
    Remove files or directories that exist only in the replica.
    """
    for file_name in comparison.right_only:
        replica_path = os.path.join(replica, file_name)

        if os.path.isdir(replica_path):
            shutil.rmtree(replica_path)
            logging.info(f"Removed directory: {replica_path}")
        else:
            os.remove(replica_path)
            logging.info(f"Removed file: {replica_path}")


def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders with logging and periodic execution.")
    parser.add_argument("source", help="Path to the source folder.")
    parser.add_argument("replica", help="Path to the replica folder.")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds.")
    parser.add_argument("log_file_path", help="Path to the log file.")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s]-[%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(args.log_file_path),  # Log to a file
            logging.StreamHandler(),  # Log to the console
        ],
    )

    logging.info("Starting folder synchronization.")

    while True:
        compare_and_sync_folders(args.source, args.replica, args.log_file_path)
        logging.info(f"Synchronization completed. Waiting for next cycle after {args.interval} sec")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
