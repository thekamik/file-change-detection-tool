# File Change Detection Tool

A lightweight tool designed to detect modifications in files with simplicity. Ideal for analyzing malware or identifying unauthorized alterations.

## Usage

```bash
mdt.py [-h] [-n] [-a] [-o ONE] [-s] [-d DIR] [-r REMOVE]
```

## Features

- **Create New Database**: `-n`, `--new` option to initiate a new database.
- **Save All Changes**: `-a`, `--all` option to store all changes in the database.
- **Save Single File**: `-o ONE`, `--one ONE` option to save a single file in the database (`python mdt.py -one [file_path]`).
- **Scan Directories**: `-s`, `--scan` option to scan all directories in the database (`python mdt.py -scan`).
- **Add Directory Path**: `-d DIR`, `--dir DIR` option to add a new path to the database (`python mdt.py -dir [dir_path]`).
- **Remove Directory Path**: `-r REMOVE`, `--remove REMOVE` option to remove a path from the database (`python mdt.py -remove [dir_path]`).

## Author

File checking tool developed by Kamil Kuczera.
