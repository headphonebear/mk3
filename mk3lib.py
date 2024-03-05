from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.id3 import ID3, APIC
from pydub import AudioSegment
import redis
import json
import os
import re
import config


class WorkerQueue:
    mk3_source = ''
    name = ''
    # regex = '\.jpg$'
    regex = '\.flac$'
    redis = ''

    # regex = '\.jpg$|\.flac$'
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
    mk3_source = ''
    in_path = ''
    in_file = ''
    out_path = ''
    overwrite = False
    bitrate = "320"
    # bitrate = "192"
    taglist = config.taglist

    def make(self):
        # making paths
        full_path_in = self.in_path + '/' + self.in_file
        full_path_clean = full_path_in[(len(self.mk3_source)):]
        path_clean = full_path_clean[:-(len(self.in_file))]
        out_mp3 = self.out_path + path_clean
        out_mp3_full = (self.out_path + path_clean + self.in_file)[:-4] + "mp3"
        # check for mp3, check for folder, create mp3
        if os.path.isfile(out_mp3_full):
            return False
        flac_in = AudioSegment.from_file(full_path_in, "flac")
        if not os.path.exists(out_mp3):
            os.makedirs(out_mp3)
        flac_in.export(out_mp3_full, format="mp3", bitrate=self.bitrate)
        # tagging
        audio_info_flac = FLAC(full_path_in)
        audio_info_mp3 = EasyID3(out_mp3_full)
        for tag in self.taglist:
            audio_info_mp3[tag] = audio_info_flac[tag]
        audio_info_mp3.save()
        # picture
        path_cover = os.path.join(full_path_in[:-(len(self.in_file))], 'cover.jpg')
        audio_picture = ID3(out_mp3_full)
        with open(path_cover, 'rb') as albumart:
            audio_picture['APIC'] = APIC(
                encoding=3,
                mime='image/jpeg',
                type=3, desc=u'Cover',
                data=albumart.read()
            )
        audio_picture.save()
        return True
