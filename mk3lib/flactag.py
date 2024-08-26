from mutagen.flac import FLAC
import json
import config


class flactag:
    def __init__(self, mk3_source_path=config.mk3_source, in_path='', in_file=''):
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

    def read_rgid(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        audio_info_flac = FLAC(flac_fullpath)
        return audio_info_flac.tags["MUSICBRAINZ_RELEASEGROUPID"][0]

    def read_albumartist(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        audio_info_flac = FLAC(flac_fullpath)
        return audio_info_flac.tags["ALBUMARTIST"][0]
