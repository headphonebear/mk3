from mutagen.easyid3 import EasyID3
from elasticsearch import Elasticsearch
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from pydub import AudioSegment
import musicbrainzngs
import json
import os
import re
import redis
import config
import psycopg2

class WorkerQueue:

    def __init__(self, name="", mk3_source="", regex="\\.jpg$|\\.flac$"):
        self.name = name
        self.mk3_source = mk3_source
        self.redis = redis.Redis()
        self.regex = regex
        self.path = ''
        self.file = ''

    def create_queue(self):
        mk3_tree = os.walk(self.mk3_source)
        for path, directories, files in mk3_tree:
            directories.sort()
            files = sorted(files)
            for file in files:
                if re.search(self.regex, file):
                    self.redis.rpush(self.name, json.dumps((path[len(self.mk3_source):]+"/", file)))
        return True

    def get_next(self):
        from_redis = self.redis.lpop(self.name)
        if (from_redis != None):
            self.path = json.loads(from_redis)[0]
            self.file = json.loads(from_redis)[1]
            return self.path, self.file
        else:
            return 'Done'

class Mp3Compiler:

    def __init__(self, mk3_source_path="", mp3_new_path="", in_path="", in_file="", overwrite=False, bitrate="320k"):
        self.mk3_source_path = mk3_source_path
        self.mp3_new_path = mp3_new_path
        self.in_path = in_path
        self.in_file = in_file
        self.overwrite = overwrite
        self.bitrate = bitrate
        self.flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        self.mp3_fullpath = self.mp3_new_path + self.in_path + self.in_file[:-4] + "mp3"
        self.cover_fullpath = self.mk3_source_path + self.in_path + "cover.jpg"
        self.taglist = config.taglist

    def compile(self):
        flac_file = AudioSegment.from_file(self.flac_fullpath, "flac")
        flac_file.export(self.mp3_fullpath, format="mp3", bitrate=self.bitrate)
        return ()

    def copy_tags(self):
        audio_info_flac = FLAC(self.flac_fullpath)
        audio_info_mp3 = EasyID3(self.mp3_fullpath)
        for tag in self.taglist:
            audio_info_mp3[tag] = audio_info_flac[tag]
        audio_info_mp3.save()
        return ()

    def add_picture(self):
        mp3_file = MP3(self.mp3_fullpath,ID3=ID3)
        with open(self.cover_fullpath, 'rb') as the_path:
            mp3_file.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc=u'Cover',
                    data=the_path.read()
                )
            )
            mp3_file.save()
        return ()

class flactag:

    def __init__(self,mk3_source_path=config.mk3_source, in_path='', in_file=''):
        self.mk3_source_path = mk3_source_path
        self.in_path = in_path
        self.in_file = in_file

    def readfull(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        audio_info_flac = FLAC(flac_fullpath)
        return json.dumps(audio_info_flac.tags, sort_keys=True, indent=4)

    def read_songid(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        audio_info_flac = FLAC(flac_fullpath)
        return audio_info_flac.tags["MUSICBRAINZ_RELEASETRACKID"][0]

    def read_albumartistids(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        audio_info_flac = FLAC(flac_fullpath)
        return audio_info_flac.tags["MUSICBRAINZ_ALBUMARTISTID"]

    def read_albumartist(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        audio_info_flac = FLAC(flac_fullpath)
        return audio_info_flac.tags["ALBUMARTIST"][0]


class scatterbrain:

    def __init__(self):
        self.elasearch = Elasticsearch("http://localhost:9200")
        self.index_name = config.index_name
        # self.elasearch.indices.create(index=self.index_name)
        # todo: create if not present

    def drop_flac(self,song_id,tag_json_string):
        print(song_id)
        print(tag_json_string)
        self.elasearch.bulk(
            index=self.index_name,
            body=tag_json_string,
            doc_type=None
        )

class Musicbrainz:

    def __init__(self):
        self.musicbrainzngs_app = config.musicbrainzngs_app
        self.musicbrainzngs_version = config.musicbrainzngs_version
        self.musicbrainzngs_contact = config.musicbrainzngs_contact

    def handshake(self):
        musicbrainzngs.set_useragent(self.musicbrainzngs_app, self.musicbrainzngs_version, self.musicbrainzngs_contact)

    def get_rgid_from_series(self, series=''):
        rgid_list = []
        counter = 0
        result = musicbrainzngs.get_series_by_id(series, includes=['release-group-rels'])
        for rg in result['series'].get('release_group-relation-list', []):
            rgid_list.append(rg['release-group']['id'])
            counter = counter + 1
        print(counter)
        return rgid_list

    def get_rgid_from_artist(self, artist):
        rgid_list = []
        result = musicbrainzngs.browse_release_groups(artist=artist, offset=0, limit=100)
        release_groups = result.get('release-group-list', [])
        for rg in release_groups:
            if rg.get('primary-type') == "Album" and not rg.get('secondary-type-list'):
                # Fetch releases for this release group
                rgid = rg['id']
                rg_details = musicbrainzngs.get_release_group_by_id(rgid, includes=["releases"])
                releases = rg_details.get('release-group', {}).get('release-list', [])
                # Check if any release in this group is "Official"
                if any(release.get('status') == "Official" for release in releases):
                    rgid_list.append(rg['id'])
        return rgid_list

    def get_album_by_rgid(self, rgid):
        album = {}
        result = musicbrainzngs.get_release_group_by_id(rgid, includes=["artists"])
        release_group = result['release-group']
        artist_name = release_group['artist-credit'][0]['artist']['name'] if 'artist-credit' in release_group and len(release_group['artist-credit']) > 0 else "Unknown"
        first_release_date = release_group.get('first-release-date', '')
        release_year = first_release_date.split('-')[0] if first_release_date else 'Unknown'
        album['artist'] = artist_name
        album['title'] = release_group['title']
        album['year'] = release_year
        return album

class Mk3Catalog:

    def __init__(self):
        self.psql_host = config.psql_host
        self.psql_port = config.psql_port
        self.psql_dbname = config.psql_dbname
        self.psql_user = config.psql_user
        self.psql_password = config.psql_password

    def add_wanted_release(self, rgid, title, artist_id, artist_name, year):
        self.conn = psycopg2.connect(
            host=self.psql_host,
            port=self.psql_port,
            dbname=self.psql_dbname,
            user=self.psql_user,
            password=self.psql_password
            )
        cur = self.conn.cursor()
        insert_query = """
            INSERT INTO wanted_releases (rgid, title, artist_id, artist_name, year)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (rgid) DO NOTHING
        """
        try:
            cur.execute(insert_query, (rgid, title, artist_id, artist_name, year))
            self.conn.commit()
            if cur.rowcount > 0:
                return 1
            else:
                return 0
        except Exception as e:
            self.conn.rollback()
            return "Error!"
        finally:
            cur.close()
            self.conn.close()

    def grab_data(self, table):
        self.conn = psycopg2.connect(
            host=self.psql_host,
            port=self.psql_port,
            dbname=self.psql_dbname,
            user=self.psql_user,
            password=self.psql_password
        )
        cur = self.conn.cursor()
        select_query = f"SELECT * FROM {table};"
        try:
            cur.execute(select_query)
            rows = cur.fetchall()
            self.conn.commit()
            return rows
        except Exception as e:
            self.conn.rollback()
            print(f"Error: {e}")
            return "Error!"
        finally:
            cur.close()
            self.conn.close()

class CatalogQueue:

    def __init__(self):
        self.redis = redis.Redis()

    def rgid_put(self, rgid):

        if not self.redis.sismember('release_set', rgid):
            # Add ID to the set to ensure uniqueness
            self.redis.sadd('release_set', rgid)
            # Add ID to the queue
            self.redis.rpush('release_queue', rgid)
            return True  # Indicate that the ID was added
        return False  # Indicate that the ID was already present

    def rgid_get(self):

        rgid = self.redis.lpop('release_queue')
        if rgid:
            release_group_id = rgid.decode('utf-8')
            return release_group_id
        return None

