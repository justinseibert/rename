from os import listdir, getcwd, renames, remove
from os.path import isdir, isfile, join
from re import sub

initial_directory = getcwd()
remove_files = [
    '_DS_Store'
]
ignore_files = [
    'rename.py'
]

def enter_directory( directory ):
    for item in listdir( directory ):
        current = join(directory,item)
        if isdir(current):
            new_dir = join(directory,format_directory(item))
            renames(current,new_dir)
            enter_directory(new_dir)
        elif item in remove_files:
            print('*remove: '+current)
            remove(current)
        elif item in ignore_files:
            print('*ignore: '+current)
        elif isfile(current):
            new_name = join(directory, format_filename(item))
            renames(current,new_name)

def format_directory(item):
    item = item.lower()
    item = sub(r'(-|_|\'|,)+',' ',item)

    replace = r'(\s|_)+(ave\.|street|st\.|way|block)'
    item = sub(replace,r'_',item)

    add = r'(\d)(th|nd|rd)\s+'
    item = sub(add,r'\1\2_',item)

    fix = r'(chestnut|franklin)\s'
    item = sub(fix,r'\1_',item)

    remove = r'(\s+|\.|\(|_*\)|_$)'
    item = sub(remove,r'',item)

    return item



def format_filename(item):
    item = sub(r'(\s+|-+|_+|,|\')',r'',item)
    parts = item.split('.')
    parts[-1] = '.' + parts[-1].lower()

    return ''.join(parts)

def main():
    enter_directory( initial_directory )

if __name__ == '__main__':
    main()
