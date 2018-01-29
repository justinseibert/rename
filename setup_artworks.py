import csv
import sys
from rename import Rename as Rename

r = Rename()
data = []
fields = []
remove_columns = [
    'category',
    'not_used',
    'not_audio',
    'combine',
    'j_rating',
    'm_rating',
    'k_rating',
    'edit',
    'notes',
    'sync',
    'discussed_site',
    'pending',
]
remove_row = [
    'not_used',
    'combine'
]
add_columns = [
    'directory',
    'filename'
]

def filter_data(dictRead):
    for line in dictRead:
        remove = False
        for key in remove_row:
            if line[key] != '':
                remove = True

        if not remove:
            for key in remove_columns:
                del line[key]
            data.append(line)

    for col in data[0]:
        if col not in remove_columns:
            fields.append(col)

    for col in add_columns:
        fields.append(col)

def fix_data():
    for row in data:
        new_address = r.fix_address(row['address'])
        row['address'] = new_address[0]
        row['group'] = new_address[1]
        row['directory'] = r.change_directory(row['address'])
        row['filename'] = r.format_filename(row['original_file'])

def main(inputfile,outputfile):
    with open(inputfile, 'rb') as f:
        dictRead = csv.DictReader(f)

        filter_data(dictRead)
        fix_data()

    with open(outputfile, 'w') as output:
        write = csv.DictWriter(output, fieldnames=fields)
        write.writeheader()
        for row in data:
            write.writerow(row)

if __name__ == '__main__':
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]

    main(inputfile,outputfile)
