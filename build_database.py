import csv
import sqlite3
import sys
from os.path import exists, join
from os import makedirs
from shutil import copy2
from data import DataStructure

def convert(the_file):
    print('building '+the_file+'...')
    with open(D.source[the_file], 'rb') as i:
        dictRead = csv.DictReader(i)

        table = D.filter_dict_data(dictRead,D.filter[the_file])
        fields = table['fields']
        data = table['data']

        data = D.make_printable(data)

        if the_file == 'address':
            data = D.add_uid_data(data)
            data = D.fix_address_data(data)
            data = D.convert_boolean(data, ['confirmed', 'installed'])
        elif the_file == 'recordings':
            data = D.add_uid_data(data)
            data = D.fix_address_data(data)
            data = D.fix_directory_structure(data)
        elif the_file == 'artists':
            data = D.add_uid_data(data)
            data = D.sanitize_url(data)
            data = D.convert_boolean(data, ['confirmed', 'assigned', 'info_sent', 'touched_base', 'art_received'])

        D.data[the_file] = data
    i.close()

    if D.enableWrite:
        with open(D.out[the_file], 'w') as o:
            write = csv.DictWriter(o, fieldnames=fields)
            write.writeheader()
            for row in data:
                write.writerow(row)
        o.close()

def copy_audio(preformat=False):
    data = D.data['recordings']
    if preformat:
        print('preformatting audio directory...')
        D.preformat_recordings_directory(D.source['audio'])

    print('transfering audio files...')
    for row in data:
        current = join(D.source['audio'],row['formatted_file_location'],row['formatted_filename'])
        new_dir = join(D.out['audio'],row['directory'])
        new = join(new_dir,row['full_filename'])

        if not exists(new_dir):
            makedirs(new_dir)

        try:
            copy2(current,new)
        except IOError:
            print('failed: '+current+' -> '+new)

def build_db(create_tables=False):
    con = sqlite3.connect(D.out['database'])
    cur = con.cursor()
    if create_tables:
        print('creating database...')
        with open(D.source['schema']) as schema:
            cur.executescript(schema.read())
        schema.close()

    print('adding artists to database...')
    to_artist = []
    to_artist_meta = []
    artist_id = {}
    for d in D.data['artists']:
        to_artist.append((
            d['uid'],
            d['artist'],
            d['location'],
            d['website'],
            d['uid'],
        ))
        to_artist_meta.append((
            d['uid'],
            d['curator'],
            d['email'],
            d['confirmed'],
            d['assigned'],
            d['info_sent'],
            d['touched_base'],
            d['art_received'],
        ))
        artist_id[d['artist']] = d['uid'] #sets artist id lookup by artist
    cur.executemany('INSERT INTO artist (id,artist,location,website,meta) VALUES (?,?,?,?,?);', to_artist)
    cur.executemany('INSERT INTO artist_meta (id,curator,email,confirmed,assigned,info_sent,touched_base,art_received) VALUES (?,?,?,?,?,?,?,?);', to_artist_meta)

    print('adding media to database...')
    to_media = []
    to_media_meta = []
    media_id = {}
    media_artist = {}
    for d in D.data['recordings']:
        to_media.append((
            d['uid'],
            d['directory'],
            d['filename'],
            d['uid'],
        ))
        to_media_meta.append((
            d['uid'],
            d['original_file_location'],
            d['original_file'],
            d['notes'],
        ))
        media_id[d['address']+str(d['group'])] = d['uid'] #sets media id lookup by address
        media_artist[d['address']+str(d['group'])] = d['artist'] # sets artist lookup by address
    cur.executemany('INSERT INTO media (id,directory,audio,meta) VALUES (?,?,?,?);', to_media)
    cur.executemany('INSERT INTO media_meta (id,original_directory,original_filename,notes) VALUES (?,?,?,?);', to_media_meta)

    print('adding addresses to database...')
    to_address = []
    to_address_meta = []
    for d in D.data['address']:
        addr = d['address']+str(d['group'])
        artist =  media_artist[addr] # looks up artist in media table by address
        d['media'] = media_id[addr] # gets media id by address
        if len(artist) > 0:
            d['artist'] = artist_id[artist]  # gets artist id
        else:
            d['artist'] = None

        to_address.append((
            d['uid'],
            d['address'],
            d['group'], #brick
            d['lat'],
            d['lng'],
            d['artist'],
            d['media'],
            d['uid']
        ))
        to_address_meta.append((
            d['uid'],
            d['confirmed'],
            d['installed'],
            d['description'], #notes
        ))
    cur.executemany('INSERT INTO address (id,address,brick,lat,lng,artist,media,meta) VALUES (?,?,?,?,?,?,?,?);', to_address)
    cur.executemany('INSERT INTO address_meta (id,confirmed,installed,notes) VALUES (?,?,?,?);', to_address_meta)

    con.commit()
    con.close()

if __name__ == '__main__':
    data_location = sys.argv[1]
    audio_location = sys.argv[2]

    D = DataStructure(
        dataLocation=data_location,
        audioLocation=audio_location,
        enableWrite=False
    )
    convert('address')
    convert('recordings')
    convert('artists')

    copy_audio(True)

    build_db(True)

    print('complete')
