from mutagen.flac import FLAC
import json
import redis
import config

class flactag:
    def __init__(self, mk3_source_path=config.mk3_source, in_path='', in_file=''):
        self.mk3_source_path = mk3_source_path
        self.in_path = in_path
        self.in_file = in_file
        self.redis_conn = redis.Redis(host='localhost', port=6379, db=0)

    def readfull(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        cache_key = f"flac:{flac_fullpath}:full"
        cached_data = self.redis_conn.get(cache_key)
        if cached_data:
            return cached_data.decode('utf-8')
        audio_info_flac = FLAC(flac_fullpath)
        result = json.dumps(audio_info_flac.tags, sort_keys=True, indent=4)
        self.redis_conn.set(cache_key, result)
        return result

    def read_songid(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        cache_key = f"flac:{flac_fullpath}:songid"
        cached_data = self.redis_conn.get(cache_key)
        if cached_data:
            return cached_data.decode('utf-8')
        audio_info_flac = FLAC(flac_fullpath)
        result = audio_info_flac.tags["MUSICBRAINZ_RELEASETRACKID"][0]
        self.redis_conn.set(cache_key, result)
        return result

    def read_albumartistids(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        cache_key = f"flac:{flac_fullpath}:albumartistids"
        cached_data = self.redis_conn.get(cache_key)
        if cached_data:
            return json.loads(cached_data.decode('utf-8'))
        audio_info_flac = FLAC(flac_fullpath)
        result = audio_info_flac.tags["MUSICBRAINZ_ALBUMARTISTID"]
        self.redis_conn.set(cache_key, json.dumps(result))  # Cache as JSON
        return result

    def read_rgid(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        cache_key = f"flac:{flac_fullpath}:rgid"
        cached_data = self.redis_conn.get(cache_key)
        if cached_data:
            return cached_data.decode('utf-8')
        audio_info_flac = FLAC(flac_fullpath)
        result = audio_info_flac.tags["MUSICBRAINZ_RELEASEGROUPID"][0]
        self.redis_conn.set(cache_key, result)
        return result

    def read_albumartist(self):
        flac_fullpath = self.mk3_source_path + self.in_path + self.in_file
        cache_key = f"flac:{flac_fullpath}:albumartist"
        cached_data = self.redis_conn.get(cache_key)
        if cached_data:
            return cached_data.decode('utf-8')
        audio_info_flac = FLAC(flac_fullpath)
        result = audio_info_flac.tags["ALBUMARTIST"][0]
        self.redis_conn.set(cache_key, result)
        return result
