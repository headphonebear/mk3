import os
import config

# Walk through the directory and its subdirectories

mk3_tree = os.walk(config.mk3_source)

for path, directories, files in mk3_tree:
    directories.sort()
    files = sorted(files)
    for file in files:
        print(path, file)

