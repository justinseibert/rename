from os.path import join, isdir, isfile
from os import listdir, renames, remove
from kml2csv import KMLtoCSV
from rename import Rename

class DataFilter(object):
    def __init__(self,Col=[],rmRow={},adCol=[]):
        self.data = []
        self.fields = []
        self.preserve_columns = Col
        self.remove_row = rmRow
        self.add_columns = adCol

class DataStructure(object):
    def __init__(self,dataLocation='data/',audioLocation='recordings/',enableWrite=True):
        self.enableWrite = enableWrite
        self.source = {
            'recordings': join(dataLocation,'_recordings.csv'),
            'artists': join(dataLocation,'_artists.csv'),
            'map': join(dataLocation,'_map.kml'),
            'address': join(dataLocation,'_addresses.csv'),
            'audio': audioLocation,
            'schema': join(dataLocation, '_schema.sql')
        }
        self.out = {
            'recordings': join(dataLocation,'recordings.csv'),
            'artists': join(dataLocation,'artists.csv'),
            'map': KMLtoCSV(self.source['map'],self.source['address']), #outputs to source[address]
            'address': join(dataLocation,'addresses.csv'),
            'audio': join(audioLocation,'audio/'),
            'database': join(dataLocation,'wrmota.db')
        }
        self.filter = {
            'address': DataFilter(
                Col = [
                    'address',
                    'lat',
                    'lng',
                    'artist',
                    'confirmed',
                    'installed',
                    'description',
                ],
                adCol = [
                    'uid',
                    'group',
                ]
            ),
            'recordings': DataFilter(
                Col = [
                    'original_file_location',
                    'original_file',
                    'address',
                    'artist',
                    'notes',
                    'category',
                ],
                rmRow = {
                    'ignore':'x',
                },
                adCol = [
                    'directory',
                    'filename',
                    'uid',
                    'formatted_file_location',
                    'formatted_filename',
                    'group'
                ]
            ),
            'artists': DataFilter(
                Col = [
                    'artist',
                    'location',
                    'curator',
                    'website',
                    'email',
                    'confirmed',
                    'assigned',
                    'info_sent',
                    'touched_base',
                    'art_received',
                ],
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

    def make_printable(self,data):
        for row in data:
            for item in row:
                row[item] = self.R.make_unicode(row[item])
        return data

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
            row['group'] = self.R.group_to_number(new_address[1])
        return data

    def fix_directory_structure(self,data):
        i = 4000
        for row in data:
            # rename directory by address
            row['directory'] = self.R.change_directory(row['address'])
            # make intermediate filename friendly
            row['formatted_filename'] = self.R.format_filename(row['original_file'])
            # adds unique alphanumeric id to filename
            row['full_filename'] = self.R.alphanumeric(i) + '_' + row['formatted_filename']
            # removes extension from filename
            row['filename'] = self.R.remove_extension(row['full_filename'])
            # makes intermediate directory friendly
            row['formatted_file_location'] = self.R.preformat_directory(row['original_file_location'])
            i += 99
        return data

    def convert_boolean(self,data,cols):
        for row in data:
            for col in cols:
                if row[col] == 'x':
                    row[col] = 1
                else:
                    row[col] = 0
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
                # print('moved: '+current+' -> '+new_name)
                renames(current,new_name)

    def filter_dict_data(self,dictRead,filter):
        fields = filter.preserve_columns
        data = []
        for line in dictRead:
            remove = False
            for key in filter.remove_row:
                # remove row if item is matches
                if line[key] == filter.remove_row[key]:
                    remove = True

            if not remove:
                new_line = {}
                for key in filter.preserve_columns:
                    new_line[key] = line[key]
                for key in filter.add_columns:
                    new_line[key] = ''
                data.append(new_line)

        for col in filter.add_columns:
            fields.append(col)

        return {
            'fields': fields,
            'data': data
        }
