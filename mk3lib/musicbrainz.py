from typing import Optional, Dict
import musicbrainzngs
import json
import redis
import config


class Musicbrainz:
    def __init__(self):
        self.musicbrainzngs_app = config.musicbrainzngs_app
        self.musicbrainzngs_version = config.musicbrainzngs_version
        self.musicbrainzngs_contact = config.musicbrainzngs_contact
        self.redis_conn = redis.Redis(host='localhost', port=6379, db=0)

    def _get_cached_data(self, key: str) -> Optional[Dict]:
        data = self.redis_conn.get(key)
        if data:
            return json.loads(data)
        return None

    def _set_cache_data(self, key: str, data: Dict, expiration: int = config.cache):
        self.redis_conn.setex(key, expiration, json.dumps(data))

    def handshake(self):
        musicbrainzngs.set_useragent(self.musicbrainzngs_app, self.musicbrainzngs_version, self.musicbrainzngs_contact)

    def get_rgid_from_series(self, series: str = ''):
        cache_key = f"series:{series}"
        cached_result = self._get_cached_data(cache_key)
        if cached_result:
            return cached_result

        rgid_list = []
        try:
            result = musicbrainzngs.get_series_by_id(series, includes=['release-group-rels'])
            for rg in result['series'].get('release_group-relation-list', []):
                rgid_list.append(rg['release-group']['id'])
        except musicbrainzngs.WebServiceError as e:
            print(f"Error fetching data: {e}")
        self._set_cache_data(cache_key, rgid_list)
        return rgid_list

    def get_rgid_from_artist(self, artist:str):
        cache_key = f"artist:{artist}"
        cached_result = self._get_cached_data(cache_key)
        if cached_result:
            return cached_result

        rgid_list = []
        try:
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
        except musicbrainzngs.WebServiceError as e:
            print(f"Error fetching data: {e}")
        self._set_cache_data(cache_key, rgid_list)
        return rgid_list

    def get_album_by_rgid(self, rgid: str) -> Dict[str, str]:
        cache_key = f"album:{rgid}"
        cached_result = self._get_cached_data(cache_key)
        if cached_result:
            return cached_result

        album = {}
        try:
            result = musicbrainzngs.get_release_group_by_id(rgid, includes=["artists"])
            release_group = result['release-group']
            artist_name = release_group['artist-credit'][0]['artist']['name'] if 'artist-credit' in release_group and len(release_group['artist-credit']) > 0 else "Unknown"
            first_release_date = release_group.get('first-release-date', '')
            release_year = first_release_date.split('-')[0] if first_release_date else 'Unknown'
            album['artist'] = artist_name
            album['title'] = release_group['title']
            album['year'] = release_year
        except musicbrainzngs.WebServiceError as e:
            print(f"Error fetching data: {e}")
        self._set_cache_data(cache_key, album)
        return album