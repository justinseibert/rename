import csv
import sqlite3
import sys
from os.path import join
from data import DataFilter
from rename import Rename

def build_database(csv,location):
    schema = join(location,'overwrite_schema.sql')
    database = join(location,'wrmota.db')

    con = sqlite3.connect(database)
    cur = con.cursor()

    print('creating database...')
    with open(schema) as schema:
        cur.executescript(schema.read())
    schema.close()

    print('adding artists to database...')
    to_artist = []
    to_artist_meta = []
    artist_id = {}
    for d in csv['artists'].data:
        to_artist.append((
            d['uid'],
            d['artist'],
            d['location'],
            d['website'],
            d['uid']
        ))
        to_artist_meta.append((
            d['uid'],
            d['curator'],
            d['email'],
            d['visitor'],
            d['confirmed'],
            d['assigned'],
            d['info_sent'],
            d['touched_base'],
            d['art_received'],
        ))
        artist_id[d['artist']] = d['uid'] #sets artist id lookup by artist
    cur.executemany('''
        INSERT INTO artist (
            id,
            artist,
            location,
            website,
            meta
        ) VALUES (?,?,?,?,?);''', to_artist)
    cur.executemany('''
        INSERT INTO artist_meta (
            id,
            curator,
            email,
            visitor,
            confirmed,
            assigned,
            info_sent,
            touched_base,
            art_received
        ) VALUES (?,?,?,?,?,?,?,?,?);''', to_artist_meta)

    print('adding media to database...')
    to_media = []
    to_media_meta = []
    media_id = {}
    media_artist = {}
    for d in csv['recordings'].data:
        to_media.append((
            d['uid'],
            d['directory'],
            d['filename'],
            d['uid'],
        ))
        to_media_meta.append((
            d['uid'],
            d['assigned'],
            d['original_file_location'],
            d['original_file'],
            d['notes'],
        ))
        media_id[d['address']+str(d['group'])] = d['uid'] #sets media id lookup by address
        media_artist[d['address']+str(d['group'])] = d['artist'] # sets artist lookup by address
    cur.executemany('''
        INSERT INTO media (
            id,
            directory,
            audio,
            meta
        ) VALUES (?,?,?,?);''', to_media)
    cur.executemany('''
        INSERT INTO media_meta (
            id,
            assigned,
            original_directory,
            original_filename,
            notes
        ) VALUES (?,?,?,?,?);''', to_media_meta)

    print('adding addresses to database...')
    to_address = []
    to_address_meta = []
    for d in csv['address'].data:
        addr = d['address']+str(d['group'])
        artist =  media_artist[addr] # looks up artist in media table by address
        d['media'] = media_id[addr] # sets media id by address
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
    cur.executemany('''
        INSERT INTO address (
            id,
            address,
            brick,
            lat,
            lng,
            artist,
            media,
            meta
        ) VALUES (?,?,?,?,?,?,?,?);''', to_address)
    cur.executemany('''
        INSERT INTO address_meta (
            id,
            confirmed,
            installed,
            notes
        ) VALUES (?,?,?,?);''', to_address_meta)

    con.commit()
    con.close()


if __name__ == '__main__':
    data_location = sys.argv[1]
    csv = {
        'address': DataFilter(
            location = data_location,
            file = 'm_addresses.csv',
            columns = [
                'uid',
                'address',
                'group',
                'lat',
                'lng',
                'confirmed',
                'installed',
                'description',
            ]
        ),
        'recordings': DataFilter(
            location = data_location,
            file = 'm_recordings.csv',
            columns = [
                'uid',
                'directory',
                'filename',
                'remove',
                'assigned',
                'artist',
                'address',
                'group',
                'category',
                'notes',
                'original_file_location',
                'original_file',
                'formatted_file_location',
                'formatted_filename',
            ],
            remove_row = {
                'remove': 1,
            }
        ),
        'artists': DataFilter(
            location = data_location,
            file = 'm_artists.csv',
            columns = [
                'uid',
                'artist',
                'location',
                'curator',
                'visitor',
                'website',
                'email',
                'confirmed',
                'assigned',
                'info_sent',
                'touched_base',
                'art_received',
            ]
        )
    }

    R = Rename()
    for sheet in csv:
        csv[sheet].build_data()

        for row in csv[sheet].data:
            for item in row:
                row[item] = R.make_unicode(row[item])
                if item == 'email':
                    row[item] = row[item].lower()

    build_database(csv,data_location)
