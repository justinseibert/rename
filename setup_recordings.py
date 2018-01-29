import csv
import sys
from re import sub, split, match, findall, compile, IGNORECASE
from setup_audio_directory import format_directory, format_filename

def make_ascii(text):
    return text.decode('unicode_escape').encode('ascii','ignore')

def fix_address(address):
    address = make_ascii(address)
    address = sub(r'street', 'St.', address, flags=IGNORECASE)
    address = sub(r'ave(\s+|$)', 'Ave.', address, flags=IGNORECASE)
    address = sub(r'(\d)(nd|rd|th)$', r'\1\2 Ave.', address, flags=IGNORECASE)
    address = sub(r'\s(n|s)\s', r' \1. ', address, flags=IGNORECASE)

    group = ''
    has_group = findall(r'[A-Z]$', address)
    if len(has_group) > 0:
        address = sub(r'[A-Z]$', '', address)
        address = sub(r'\s$', '', address)
        group = has_group[0]

    return [address,group]

def main(inputfile,outputfile):
    with open(inputfile, 'rb') as f:
        read = csv.DictReader(f)
        dict = []
        for line in read:
            new_address = fix_address(line['address'])
            line['address'] = new_address[0]
            line['group'] = new_address[1]
            line['directory'] = format_directory(line['original_file_location'])
            line['filename'] = format_filename(line['original_file'])
            dict.append(line)
        fields = [d for d in dict[0]]

        with open(outputfile, 'w') as output:
            write = csv.DictWriter(output, fieldnames=fields)
            write.writeheader()
            for row in dict:
                write.writerow(row)

if __name__ == '__main__':
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]

    main(inputfile,outputfile)
