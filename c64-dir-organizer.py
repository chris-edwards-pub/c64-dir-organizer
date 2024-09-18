import os
import shutil
import fnmatch
import argparse
import sys

"""
This script organizes files into directories based on their file types and the first character of their filenames.
It supports moving or copying files from a source directory to a destination directory, with options for recursion,
verbosity, and dry-run simulation.

Usage:
    python script_name.py [source] [destination] [-a {move,copy}] [-r] [-v] [-d]

Arguments:
    source (str): Source directory containing the files to be organized.
    destination (str): Destination base directory where files will be organized.
    -a, --action (str): Action to perform: 'move' or 'copy' files (default: 'move').
    -r, --recursive: Recursively search for files in the source directory (default: False).
    -v, --verbose: Enable verbose output showing each operation.
    -d, --dry-run: Simulate the script actions without making any changes.
    -h, --help: Show the help message and exit.

Functionality:
    - The script defines a set of main directories and their associated file extensions.
    - It walks through the source directory (recursively or non-recursively) to find files matching the defined extensions.
    - Files are organized into subdirectories within the main directories based on the first character of their filenames.
      If the first character is not an alphabet, they are placed in a '0_9' directory.
    - The script can either move or copy the files based on the specified action.
    - Verbose mode provides detailed output of each operation.
    - Dry-run mode simulates the actions without making any changes to the filesystem.

Functions:
    - create_directory_if_needed(path): Creates a directory if it doesn't exist and prints the action if verbose or dry-run is enabled.
    - move_file(source, destination_dir): Handles file move with overwrite confirmation.
    - copy_file(source, destination_dir): Handles file copy.
"""

# Define the main directories and their associated file extensions
main_dirs = {
    'D64': '.d64',
    'G64': '.g64',
    'PRG': '.prg',
    'T64': '.t64',
    'F64': '.f64',
    'CRT': '.crt',
    'TAP': '.tap',
    'D81': '.d81',
    'D71': '.d71',
}


# Function to create a directory if it doesn't exist and print the action if verbose or dry-run is enabled
def create_directory_if_needed(path):
    if not os.path.exists(path):
        if dry_run:
            if verbose:
                print(f"Simulated creation of directory: {path}")
        else:
            os.makedirs(path, exist_ok=True)
            if verbose:
                print(f"Created directory: {path}")


# Function to handle file move with overwrite confirmation
def move_file(source, destination_dir):
    destination_file = os.path.join(destination_dir, os.path.basename(source))
    # Create the destination directory if it doesn't exist
    create_directory_if_needed(destination_dir)

    if os.path.exists(destination_file):
        if verbose or dry_run:
            print(f"File already exists: {destination_file}")
        confirm = input(f"Overwrite {destination_file}? (y/n): ") if not dry_run else 'y'
        if confirm.lower() != 'y':
            if verbose:
                print(f"Skipped: {source}")
            return
        else:
            os.remove(destination_file)

    shutil.move(source, destination_file)
    if verbose:
        print(f"Moved: {source} -> {destination_file}")


# Function to handle file copy
def copy_file(source, destination_dir):
    destination_file = os.path.join(destination_dir, os.path.basename(source))

    # Create the destination directory if it doesn't exist
    create_directory_if_needed(destination_dir)

    shutil.copy(source, destination_file)
    if verbose:
        print(f"Copied: {source} -> {destination_file}")


# Set up argument parser for source, destination paths, action type, recursion, verbosity, and dry-run
parser = argparse.ArgumentParser(
    description='Organize files into directories based on file types and first character.',
    add_help=False  # Disable the default help to customize behavior
)

# Define the main arguments with short versions
parser.add_argument('source', type=str, nargs='?', help='Source directory containing the files')
parser.add_argument('destination', type=str, nargs='?', help='Destination base directory')
parser.add_argument('-a', '--action', type=str, choices=['move', 'copy'], default='move', help='Action to perform: move or copy files (default: move)')
parser.add_argument('-r', '--recursive', action='store_true', default=False, help='Recursively search for files (default: False)')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output showing each operation')
parser.add_argument('-d', '--dry-run', action='store_true', help='Simulate the script actions without making changes')
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')

# Check if no arguments are provided
if len(sys.argv) == 1:
    print("Usage: python script_name.py [source] [destination] [-a {move,copy}] [-r] [-v] [-d]")
    print("Use '--help' or '-h' to see all available options.")
    sys.exit(1)

# Parse the arguments
args = parser.parse_args()

# Check if required arguments are missing
if not args.source or not args.destination:
    print("Error: Both 'source' and 'destination' paths are required.")
    print("Usage: python script_name.py [source] [destination] [-a {move,copy}] [-r] [-v] [-d]")
    sys.exit(1)

# Define the base source and destination directories from arguments
source_directory = args.source
base_directory = args.destination
action = args.action
recursive = args.recursive
verbose = args.verbose or args.dry_run  # Enable verbose mode if dry-run is active
dry_run = args.dry_run

# Walk through directories recursively or non-recursively
for main_dir, extension in main_dirs.items():
    main_dir_path = os.path.join(base_directory, main_dir)

    for root, _, files in os.walk(source_directory):
        for file in files:
            if fnmatch.fnmatch(file.lower(), f'*{extension}'):  # Case-insensitive match
                first_char = os.path.basename(file)[0].upper()
                destination_dir = os.path.join(main_dir_path, first_char if first_char.isalpha() else '0_9')

                source_file = os.path.join(root, file)

                # Simulate or perform move/copy based on the action argument
                if dry_run:
                    print(f"Simulated {'move' if action == 'move' else 'copy'}: {source_file} -> {destination_dir}")
                else:
                    if action == 'move':
                        move_file(source_file, destination_dir)
                    elif action == 'copy':
                        copy_file(source_file, destination_dir)

        # If not recursive, break after the first level
        if not recursive:
            break
