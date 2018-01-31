from bs4 import BeautifulSoup
import csv
from re import sub
import sys

class KMLtoCSV(object):
    def __init__(self, inputfile, outputfile):
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.columns = [
            'address',
            'lat',
            'lng'
        ]

        with open(self.inputfile, 'r') as f:
            kml = BeautifulSoup(f, 'xml')
            with open(self.outputfile, 'w') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.add_data_columns(kml))

                self.populate_data(kml,writer)

    def add_data_columns(self,kml):
        for pm in kml.find_all('Placemark',limit=1): #other data columns
            for child in pm.contents[7].find_all('Data'):
                self.columns.append(child['name'])

        return self.columns

    def populate_data(self,kml,writer):
        for pm in kml.find_all('Placemark'):
            data = []
            coords = pm.contents[9].coordinates.string
            coords = sub(r'(\n|\s)+','',coords).split(',')

            data.append(pm.contents[1].string) # address
            data.append(coords[1]) # lat
            data.append(coords[0]) # lng

            for child in pm.contents[7].find_all('Data'): #other data
                val = child.find('value').string
                if val == None or val == '' or val == '0':
                    val = ''
                elif val == '1' or val == 'x' or val.lower() == 'yes' or val.lower() == 'true':
                    val = 'x'
                data.append(val)

            writer.writerow([unicode(d).encode("utf-8") for d in data])
