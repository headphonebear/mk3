from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3, APIC
from pydub import AudioSegment
import json
import os
import re
import config


class WorkerQueue:

    def __init__(self, name="", mk3_source="", redis="", regex="\.jpg$|\.flac$"):
        self.name = name
        self.mk3_source = mk3_source
        self.redis = redis
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
                    self.redis.rpush(self.name, json.dumps((path, file)))
        return True

    def get_next(self):
        from_redis = self.redis.lpop(self.name)
        # todo fix error on empty return
        self.path = json.loads(from_redis)[0]
        self.file = json.loads(from_redis)[1]
        return self.path, self.file

class Mp3Compiler:

    def __init__(self, mk3_source="", out_path="", overwrite=False, bitrate="320k"):
        self.mk3_source = mk3_source
        self.out_path = out_path
        self.overwrite = overwrite
        self.bitrate = bitrate
        self.taglist = config.taglist
        self.in_path = ''
        self.in_file = ''

        self.full_path_in = self.in_path + '/' + self.in_file
        self.full_path_clean = -self.full_path_in[(len(self.mk3_source)):]
        self.path_clean =self.full_path_clean[:-(len(self.in_file))]
        self.out_mp3 = self.out_path + self.path_clean
        self.out_mp3_full = (self.out_path + path_clean + self.in_file)[:-4] + "mp3"

    def probe_file(self):
        if os.path.isfile(self.out_mp3_full):
            return True
        else:
            return False

    def probe_folder(self):
        if not os.path.exists(self.out_mp3):
            os.makedirs(self.out_mp3)
        return ()

    def compile(self):
        flac_in = AudioSegment.from_file(self.full_path_in, "flac")
        flac_in.export(self.out_mp3_full, format="mp3", bitrate=self.bitrate)
        return ()

    def copy_tags(self):
        audio_info_flac = FLAC(self.full_path_in)
        audio_info_mp3 = EasyID3(self.out_mp3_full)
        for tag in self.taglist:
            audio_info_mp3[tag] = audio_info_flac[tag]
        audio_info_mp3.save()
        return ()

    def add_picture(self):
        audio_picture = ID3(self.out_mp3_full)
        path_cover = os.path.join(self.full_path_in[:-(len(self.in_file))], 'cover.jpg')
        with open(path_cover, 'rb') as albumart:
            audio_picture['APIC'] = APIC(
                encoding=3,
                mime='image/jpeg',
                type=3, desc=u'Cover',
                data=albumart.read()
            )
        audio_picture.save()
        return ()