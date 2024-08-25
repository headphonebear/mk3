from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from pydub import AudioSegment
import config


class Mp3Compiler:
    def __init__(self, mk3_source_path:str="", mp3_new_path:str="", in_path:str="", in_file:str="", overwrite=False, bitrate:str="320k"):
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
