from os import listdir, renames, remove
from os.path import isdir, isfile, join
from re import sub
from rename import Rename as Rename

remove_files = [
    '_DS_Store'
]
ignore_files = [
    'rename.py'
]

def enter_directory(directory):
    for item in listdir(directory):
        current = join(directory,item)
        if isdir(current):
            new_dir = join(directory,Rename.format_directory(item))
            print(new_dir)
            # renames(current,new_dir)
            enter_directory(new_dir)
        elif item in remove_files:
            print('*remove: '+current)
            remove(current)
        elif item in ignore_files:
            print('*ignore: '+current)
        elif isfile(current):
            new_name = join(directory, Rename.format_filename(item))
            print(new_name)
            # renames(current,new_name)

if __name__ == '__main__':
    initial_directory = sys.argv[1]
    enter_directory(initial_directory)
