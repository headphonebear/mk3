"""PostgreSQL upserts for the mk3 core catalog (albums / tracks / track_paths).

Design notes:
  - ONE connection for the whole run (the legacy mk3catalog opened a fresh
    connection per insert — ~22k connections would crawl).
  - Upserts use ON CONFLICT DO UPDATE so a *second* run picks up tag fixes made
    in Picard, instead of silently ignoring them.
  - Per-file SAVEPOINT (see tools/index.py): one bad FLAC rolls back only its
    own three rows, never the whole batch.
"""
import psycopg2
import config


class Catalog:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=config.psql_host,
            port=config.psql_port,
            dbname=config.psql_dbname,
            user=config.psql_user,
            password=config.psql_password,
        )
        self.cur = self.conn.cursor()

    # ── albums ──────────────────────────────────────────────────────────────
    def upsert_album(self, a: dict):
        self.cur.execute(
            """
            INSERT INTO albums (
                rgid, release_mbid, title, album_artist, album_artist_sort,
                album_artist_mbid, original_date, original_year, primary_type,
                label, catalog_number, barcode, release_country, media,
                total_discs, total_tracks
            ) VALUES (
                %(rgid)s, %(release_mbid)s, %(title)s, %(album_artist)s,
                %(album_artist_sort)s, %(album_artist_mbid)s, %(original_date)s,
                %(original_year)s, %(primary_type)s, %(label)s,
                %(catalog_number)s, %(barcode)s, %(release_country)s, %(media)s,
                %(total_discs)s, %(total_tracks)s
            )
            ON CONFLICT (rgid) DO UPDATE SET
                release_mbid      = EXCLUDED.release_mbid,
                title             = EXCLUDED.title,
                album_artist      = EXCLUDED.album_artist,
                album_artist_sort = EXCLUDED.album_artist_sort,
                album_artist_mbid = EXCLUDED.album_artist_mbid,
                original_date     = EXCLUDED.original_date,
                original_year     = EXCLUDED.original_year,
                primary_type      = EXCLUDED.primary_type,
                label             = EXCLUDED.label,
                catalog_number    = EXCLUDED.catalog_number,
                barcode           = EXCLUDED.barcode,
                release_country   = EXCLUDED.release_country,
                media             = EXCLUDED.media,
                total_discs       = EXCLUDED.total_discs,
                total_tracks      = EXCLUDED.total_tracks
            """,
            a,
        )

    # ── tracks ──────────────────────────────────────────────────────────────
    def upsert_track(self, t: dict):
        self.cur.execute(
            """
            INSERT INTO tracks (
                release_track_mbid, rgid, recording_mbid, title, artist,
                artist_sort, artist_mbid, disc_number, track_number, isrc, acoustid
            ) VALUES (
                %(release_track_mbid)s, %(rgid)s, %(recording_mbid)s, %(title)s,
                %(artist)s, %(artist_sort)s, %(artist_mbid)s::uuid[], %(disc_number)s,
                %(track_number)s, %(isrc)s, %(acoustid)s
            )
            ON CONFLICT (release_track_mbid) DO UPDATE SET
                rgid           = EXCLUDED.rgid,
                recording_mbid = EXCLUDED.recording_mbid,
                title          = EXCLUDED.title,
                artist         = EXCLUDED.artist,
                artist_sort    = EXCLUDED.artist_sort,
                artist_mbid    = EXCLUDED.artist_mbid,
                disc_number    = EXCLUDED.disc_number,
                track_number   = EXCLUDED.track_number,
                isrc           = EXCLUDED.isrc,
                acoustid       = EXCLUDED.acoustid
            """,
            t,
        )

    # ── track_paths ─────────────────────────────────────────────────────────
    def upsert_path(self, release_track_mbid: str, relpath: str, filesize: int):
        self.cur.execute(
            """
            INSERT INTO track_paths (release_track_mbid, relpath, filesize)
            VALUES (%s, %s, %s)
            ON CONFLICT (release_track_mbid) DO UPDATE SET
                relpath  = EXCLUDED.relpath,
                filesize = EXCLUDED.filesize
            """,
            (release_track_mbid, relpath, filesize),
        )

    # ── per-file transaction control (SAVEPOINT) ────────────────────────────
    def savepoint(self):
        self.cur.execute("SAVEPOINT f")

    def release(self):
        self.cur.execute("RELEASE SAVEPOINT f")

    def rollback_file(self):
        self.cur.execute("ROLLBACK TO SAVEPOINT f")

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
