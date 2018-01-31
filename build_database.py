import csv
import sys
from os.path import join, exists, isdir, isfile
from os import makedirs, listdir, renames, remove
from shutil import copy2
from rename import Rename
from kml2csv import KMLtoCSV

class DataFilter(object):
    def __init__(self,rmCol=[],rmRow={},adCol=[]):
        self.data = []
        self.fields = []
        self.remove_columns = rmCol
        self.remove_row = rmRow
        self.add_columns = adCol

class DataStructure(object):
    def __init__(self,dataLocation='data/',audioLocation='recordings/',enableWrite=True):
        self.enableWrite = enableWrite
        self.source = {
            'recordings': join(data_location,'_recordings.csv'),
            'artists': join(data_location,'_artists.csv'),
            'map': join(data_location,'_map.kml'),
            'address': join(data_location,'_addresses.csv'),
            'audio': audio_location
        }
        self.out = {
            'recordings': join(data_location,'recordings.csv'),
            'artists': join(data_location,'artists.csv'),
            'map': KMLtoCSV(self.source['map'],self.source['address']), #outputs to source[address]
            'address': join(data_location,'addresses.csv'),
            'audio': join(audio_location,'audio/')
        }
        self.filter = {
            'address': DataFilter(
                rmCol = [
                    'sample',
                    'confirmed',
                    'interviewed',
                    'site photos',
                    'group site',
                    'student'
                ],
                adCol = [
                    'group',
                    'uid'
                ]
            ),
            'recordings': DataFilter(
                rmCol = [
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
                    'id'
                ],
                rmRow = {
                    'not_used':'',
                    'combine':''
                },
                adCol = [
                    'directory',
                    'filename',
                    'uid',
                    'formatted_file_location'
                ]
            ),
            'artists': DataFilter(
                rmCol = [
                    'info_sent',
                    'touched base',
                    'art_received'
                ],
                rmRow = {
                    'confirmed':'x',
                    'assigned':'x'
                },
                adCol=[
                    'uid'
                ]
            )
        }
        self.data = {
            'address': [],
            'recordings': [],
            'artists': []
        }
        self.R = Rename()

    def add_uid_data(self,data):
        uid = 0
        for row in data:
            row['uid'] = uid
            uid += 1
        return data

    def fix_address_data(self,data):
        for row in data:
            new_address = self.R.fix_address(row['address'])
            row['address'] = new_address[0]
            row['group'] = new_address[1]
        return data

    def fix_directory_structure(self,data):
        for row in data:
            row['directory'] = self.R.change_directory(row['address'])
            row['filename'] = self.R.format_filename(row['original_file'])
            row['formatted_file_location'] = self.R.preformat_directory(row['original_file_location'])
            print(row['formatted_file_location'])
        return data

    def sanitize_url(self,data):
        for row in data:
            row['website'] = self.R.simplify_website(row['website'])
        return data

    def preformat_recordings_directory(self,directory):
        remove_files = [
            '_DS_Store'
        ]
        ignore_files = [
            'rename.py'
        ]
        for item in listdir(directory):
            current = join(directory,item)
            if isdir(current):
                new_dir = join(directory,self.R.preformat_directory(item))
                renames(current,new_dir)
                self.preformat_recordings_directory(new_dir)
            elif item in remove_files:
                print('*remove: '+current)
                remove(current)
            elif item in ignore_files:
                print('*ignore: '+current)
            elif isfile(current):
                new_name = join(directory,self.R.format_filename(item))
                renames(current,new_name)

    def filter_dict_data(self,dictRead,filter):
        fields = []
        data = []
        for line in dictRead:
            remove = False
            for key in filter.remove_row:
                # remove row if item is not blank
                if line[key] != filter.remove_row[key]:
                    remove = True

            if not remove:
                for key in filter.remove_columns:
                    del line[key]
                data.append(line)

        for col in data[0]:
            if col not in filter.remove_columns:
                fields.append(col)

        for col in filter.add_columns:
            fields.append(col)

        return {
            'fields': fields,
            'data': data
        }

def convert(the_file):
    with open(D.source[the_file], 'rb') as i:
        dictRead = csv.DictReader(i)

        table = D.filter_dict_data(dictRead,D.filter[the_file])
        fields = table['fields']
        data = table['data']

        if the_file == 'address':
            data = D.add_uid_data(data)
            data = D.fix_address_data(data)
            D.data[the_file] = data
        elif the_file == 'recordings':
            data = D.add_uid_data(data)
            data = D.fix_address_data(data)
            data = D.fix_directory_structure(data)
        elif the_file == 'artists':
            data = D.add_uid_data(data)
            data = D.sanitize_url(data)

        D.data[the_file] = data

    if D.enableWrite:
        with open(D.out[the_file], 'w') as o:
            write = csv.DictWriter(o, fieldnames=fields)
            write.writeheader()
            for row in data:
                write.writerow(row)

def copy_audio(preformat=False):
    data = D.data['recordings']
    if preformat:
        D.preformat_recordings_directory(D.source['audio'])

    for row in data:
        current = join(D.source['audio'],row['formatted_file_location'],row['filename'])
        new_dir = join(D.out['audio'],row['directory'])
        new = join(new_dir,row['filename'])

        if not exists(new_dir):
            makedirs(new_dir)

        try:
            copy2(current,new)
        except IOError:
            print('failed: '+current+' -> '+new)


if __name__ == '__main__':
    data_location = sys.argv[1]
    audio_location = sys.argv[2]

    D = DataStructure(
        dataLocation=data_location,
        audioLocation=audio_location,
        enableWrite=True
    )
    # convert('address')
    convert('recordings')
    # convert('artists')
    #
    copy_audio(False)
