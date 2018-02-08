import csv
from os.path import join

class DataFilter(object):
    def __init__(self,location,file,columns=[],remove_row={},add_columns={}):
        self.file = join(location,file),
        self.data = []
        self.fields = []
        self.columns = columns
        self.remove_row = remove_row
        self.add_columns = add_columns

    def build_data(self):
        print(self.file)
        with open(self.file[0], 'rb') as i:
            dictRead = csv.DictReader(i)

            fields = self.columns
            data = []
            for line in dictRead:
                remove = False
                for key in self.remove_row:
                    # remove row if item matches
                    if line[key] == self.remove_row[key]:
                        remove = True

                if not remove:
                    new_line = {}
                    for key in self.columns:
                        new_line[key] = line[key]
                    for key in self.add_columns:
                        new_line[key] = ''
                    data.append(new_line)

            for col in self.add_columns:
                fields.append(col)

            self.fields = fields
            self.data = data
