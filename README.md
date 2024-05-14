# file-change-detection-tool
Tool to detect changes in files in a simple way. It can be used to analyze malware or detect unauthorized modifications.

usage: mdt.py [-h] [-n] [-a] [-o ONE] [-s] [-d DIR] [-r REMOVE]

file checking tool by Kamil Kuczera

options:                          descriptions:
  -h, --help                      show this help message and exit
  -n, --new                       create new database (python mdt.py -new)
  -a, --all                       save all changes in database (python mdt.py -all)
  -o ONE, --one ONE               save one file in database (python mdt.py -one [file_path])
  -s, --scan                      scan all directories in database (python mdt.py -scan)
  -d DIR, --dir DIR               add new path to a database (python mdt.py -dir [dir_path])
  -r REMOVE, --remove REMOVE      remove path from database (python mdt.py -remove [dir_path])
