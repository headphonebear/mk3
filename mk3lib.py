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
        return audio_info_flac.tags["MUSICBRAINZ_RELEASETRACKID"]

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
        result = musicbrainzngs.get_series_by_id(series, includes=['release-group-rels'])
        for rg in result['series'].get('release_group-relation-list', []):
            rgid_list.append(rg['release-group']['id'])
        return rgid_list

    def get_rgid_from_artist(self, artist):
        rgid_list = []

        result = musicbrainzngs.browse_release_groups(artist=artist, offset=0, limit=100)
        release_groups = result.get('release-group-list', [])

        for rg in release_groups:
            if rg.get('primary-type') == "Album" and not rg.get('secondary-type-list'):
                # Fetch releases for this release group
                rg_id = rg['id']
                rg_details = musicbrainzngs.get_release_group_by_id(rg_id, includes=["releases"])
                releases = rg_details.get('release-group', {}).get('release-list', [])

                # Check if any release in this group is "Official"
                if any(release.get('status') == "Official" for release in releases):
                    rgid_list.append(rg['id'])
        return rgid_list
