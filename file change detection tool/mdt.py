import os
import argparse
import hashlib
import sqlite3
from collections import namedtuple

file_data = namedtuple('file_data', 'path hash')

def calculate_hash(path, hash_method):
    # Select right hash function
    if hash_method == "SHA256":
        hash_method = hashlib.sha256()
    elif hash_method == "SHA512":
        hash_method = hashlib.sha512()
    else:
        raise Exception("Method not supported")
    
    with open(path, "rb") as file:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: file.read(4096), b""):
            hash_method.update(byte_block)
    return hash_method.hexdigest()


def find_files(path, hash_method="SHA256"):
    # lists to store elements in actual path
    files = []
    folders = []

    # lists to store all folders and files.
    all_files = []
    all_folders = []

    # Walk through the directory
    for entry in os.scandir(path):
        if entry.is_file():
            # find full path
            file_path = os.path.join(path, entry.name)

            # calculate file hash
            file_hash = calculate_hash(file_path, hash_method)
            
            # Add namedtuple to files list
            files.append(file_data(file_path, file_hash))
        elif entry.is_dir():
            # Add to folders list
            folders.append(entry.name)

            # Recursive call function, to scan subdirectories
            folder_path = os.path.join(path, entry.name)
            new_files, new_folders = find_files(folder_path)
            all_folders.extend(new_folders)
            all_files.extend(new_files)
        
    # Add files and folders from main run
    all_folders.extend(folders)
    all_files.extend(files)

    # return all files and subdirectories
    return all_files, all_folders


def create_db(db_path):
    # Create new db
    if os.path.exists(db_path):
        return "database already exist"
    else:
        # Create and open new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table - OLD
        cursor.execute('''CREATE TABLE old_files
                    (path TEXT PRIMARY KEY, 
                    hash TEXT NOT NULL)''')

        # Create table - NEW
        cursor.execute('''CREATE TABLE new_files
                    (path TEXT PRIMARY KEY, 
                    hash TEXT NOT NULL)''')

        # Create table - PATH
        cursor.execute('''CREATE TABLE root_dir
                    (id INTEGER PRIMARY KEY, 
                    path TEXT NOT NULL)''')

        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()
    return "new database created"


def read_new_files(db_path):
    # Read files and save them to a database
    if os.path.exists(db_path) == False:
        return "database does not exist"

    # Connect to the database 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT path FROM root_dir')

    # Fetch all results
    all_paths = cursor.fetchall()

    # Create return message buffer
    return_message = "OK"

    # Delete all rows from the table
    cursor.execute('DELETE FROM new_files')

    # Scan all directories from database
    for root_directory in all_paths:

        # Check if path exist
        if os.path.exists(root_directory[0]) == False:
            # Close the connection
            conn.close()

            # End function
            return f"path {root_directory[0]} does not exist"

        # Scan directories
        files, folders = find_files(root_directory[0])

        # Insert data from the list of namedtuples
        for item in files:
            try:
                cursor.execute('INSERT INTO new_files (path, hash) VALUES (?, ?)', (item.path, item.hash))
            except Exception as ex:
                return_message = ex

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    # Return true - end of function
    return return_message


def compare_files(db_path, save_to_file=False):
    # Compares files with db, updates file status
    if os.path.exists(db_path) == False:
        return "create database first"

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to find rows that are in both tables with different column values
    cursor.execute('''
        SELECT a.path, a.hash, b.hash
        FROM old_files a
        INNER JOIN new_files b ON a.path = b.path
        WHERE a.hash != b.hash
    ''')
    different_values = cursor.fetchall()

    # Query to find rows that are only in table1
    cursor.execute('''
        SELECT path, hash
        FROM old_files
        WHERE path NOT IN (SELECT path FROM new_files)
    ''')
    only_in_old = cursor.fetchall()

    # Query to find rows that are only in table2
    cursor.execute('''
        SELECT path, hash
        FROM new_files
        WHERE path NOT IN (SELECT path FROM old_files)
    ''')
    only_in_new = cursor.fetchall()

    # Close the connection
    conn.close()

    # Create a log list
    log_list = []

    # Modified files
    for file_path, old_hash, new_hash in different_values:
        log_list.append(f'File: {file_path} has been modified')

    # Files deleted
    for file_path, old_hash in only_in_old:
        log_list.append(f'File: {file_path} has been deleted')

    # New files
    for file_path, new_hash in only_in_new:
        log_list.append(f'File: {file_path} has been added')

    return log_list


def accept_files(db_path, selected_file=None):
    # Saves all new entries to a db
    # Read files and save them to a database
    if os.path.exists(db_path) == False:
        return "create database first"

    # Connect to the database 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all results
    all_paths = cursor.fetchall()

    # Create return message buffer
    return_message = "OK"

    # Try to update table
    try:
        if selected_file == None:
            # Delete all rows from the table
            cursor.execute('DELETE FROM old_files')

            # Insert data from new_table to old_table
            cursor.execute(f'''
                INSERT INTO old_files
                SELECT * FROM new_files;
            ''')
        else:
            cursor.execute('DELETE FROM old_files WHERE path = ?;', (selected_file, ))

            # Insert new item to old_table
            cursor.execute(f'''
                INSERT INTO old_files
                SELECT * FROM new_files WHERE path = ?
            ''', (selected_file,))
    except Exception as ex:
        return_message = ex

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    # Return true - end of function
    return return_message


def add_new_path(db_path, new_path):
    # Replace old hash with new hash
    if os.path.exists(db_path) == False:
        return "create database first"
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the path is already in the 'root_dir' table
    cursor.execute('SELECT * FROM root_dir WHERE path = ?', (new_path,))
    result = cursor.fetchone()

    # Create result flag
    return_flag = "Path already in db"
    # If result is None, the path is not in the table
    if result is None:
        cursor.execute('INSERT INTO root_dir (path) VALUES (?)', (new_path,))
        conn.commit()
        # Path inserted successfully.
        return_flag = "New path added"
    
    # Close connection and return value
    conn.close()
    return return_flag


def remove_path(db_path, remove_path):
    # Remove path from db
    if os.path.exists(db_path) == False:
        return "create database first"
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    output_message = "OK"

    # Remove path from db
    try:
        cursor.execute('DELETE FROM root_dir WHERE path = ?;', (remove_path, ))
        conn.commit()
    except Exception as ex:
        output_message = ex
    
    # Close connection and return value
    conn.close()
    return output_message


if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser(description='file checking tool by Kamil Kuczera')

    # Add parameters
    parser.add_argument('-n', '--new', action='store_true', help='create new database (python mdt.py -new)')
    parser.add_argument('-a', '--all', action='store_true', help='save all changes in database (python mdt.py -all)')
    parser.add_argument('-o', '--one', action='store', help='save one file in database (python mdt.py -one [file_path])')
    parser.add_argument('-s', '--scan', action='store_true', help='scan all directories in database (python mdt.py -scan)')
    parser.add_argument('-d', '--dir', action='store', help='add new path to a database (python mdt.py -dir [dir_path])')
    parser.add_argument('-r', '--remove', action='store', help='remove path from database (python mdt.py -remove [dir_path])')

    # Parse the arguments
    args = parser.parse_args()

    # Handle user input
    if args.new:
        result = create_db("files.db")
        print(result)

    if args.all:
        result = accept_files("files.db")
        print(result)

    if args.one:
        result = accept_files("files.db", args.one)
        print(result)

    if args.scan:
        # Compare Files
        read_message = read_new_files("files.db")
        if read_message == "OK":
            log_list = compare_files("files.db")
            for log in log_list:
                print(log)
            if log_list == []:
                print("No errors found")
        else:
            print(read_message)

    if args.dir:
        result = add_new_path("files.db", args.dir)
        print(result)

    if args.remove:
        result = remove_path("files.db", args.remove)
        print(result)
