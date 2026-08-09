-- ╔══════════════════════════════════════════════════════════════════════════╗
-- ║  mk3 — core catalog schema                                                 ║
-- ║  The CDs on the wall, as data. Filled by the runner from FLAC tags ONLY.   ║
-- ╚══════════════════════════════════════════════════════════════════════════╝
--
-- Two core tables + a storage sidecar. Everything here comes 1:1 from the FLAC
-- Vorbis tags — nothing is loaded from the network. Keys are MusicBrainz IDs,
-- so the mk3 policy is enforced by the schema itself: UUID columns reject any
-- non-MBID junk, and a missing Release Group / Release-Track ID simply cannot
-- be inserted (they are the primary keys).
--
-- Grain:
--   albums  — keyed by Release Group   (the album concept; "does mk3 have X?")
--   tracks  — keyed by Release-Track ID (this track ON this release
--             → exactly one physical FLAC each)
--
-- NOTE: the old shopping-list tables (wanted_releases / wanted_artists /
-- wanted_series / owned_releases) are intentionally NOT carried over. `owned`
-- is now simply "a row exists in albums"; the wanted/shopping-list side is a
-- separate future thread and will get its own MBID-clean schema when we build
-- it. (Old definitions live in git history.)

-- ── albums — one row per owned Release Group ────────────────────────────────
CREATE TABLE albums (
    rgid              UUID PRIMARY KEY,   -- MUSICBRAINZ_RELEASEGROUPID (the album)
    release_mbid      UUID NOT NULL,      -- MUSICBRAINZ_ALBUMID  (the specific release we own)
    title             TEXT NOT NULL,      -- ALBUM
    album_artist      TEXT NOT NULL,      -- ALBUMARTIST (display)
    album_artist_sort TEXT,               -- ALBUMARTISTSORT
    album_artist_mbid UUID,               -- MUSICBRAINZ_ALBUMARTISTID  (see multi-value note below)
    original_date     TEXT,               -- ORIGINALDATE ("1980-09")
    original_year     INT,                -- ORIGINALYEAR (cheap sort key)
    primary_type      TEXT,               -- RELEASETYPE ("album"/"single"/…)
    -- physical-CD details: strictly these are release-level, but the
    -- "one CD per Release Group" policy keeps them unambiguous per row.
    label             TEXT,               -- LABEL
    catalog_number    TEXT,               -- CATALOGNUMBER
    barcode           TEXT,               -- BARCODE
    release_country   TEXT,               -- RELEASECOUNTRY
    media             TEXT,               -- MEDIA ("CD")
    total_discs       INT,                -- TOTALDISCS
    total_tracks      INT                 -- TOTALTRACKS
);

-- ── tracks — one row per owned track (= one physical FLAC) ───────────────────
CREATE TABLE tracks (
    release_track_mbid UUID PRIMARY KEY,          -- MUSICBRAINZ_RELEASETRACKID (unique per instance)
    rgid               UUID NOT NULL REFERENCES albums(rgid),
    recording_mbid     UUID,                      -- MUSICBRAINZ_TRACKID (the recording; shared across releases)
    title              TEXT NOT NULL,             -- TITLE
    artist             TEXT NOT NULL,             -- ARTIST (may differ from album_artist: feat./classical)
    artist_sort        TEXT,                      -- ARTISTSORT
    artist_mbid        UUID[],                    -- MUSICBRAINZ_ARTISTID (array: feat. tracks credit >1 artist → keep them all, searchable)
    disc_number        INT,                       -- DISCNUMBER
    track_number       INT,                       -- TRACKNUMBER
    isrc               TEXT,                      -- ISRC
    acoustid           UUID                       -- ACOUSTID_ID (audio fingerprint → future similarity work)
);

-- WHY an explicit index: a FK does not create one on its own, and
-- "give me every track of this album" is THE hot query.
CREATE INDEX tracks_rgid_idx ON tracks (rgid);

-- GIN index so array-containment stays fast: "every track involving artist X"
-- is  WHERE artist_mbid @> ARRAY['<mbid>']::uuid[]  — the whole point of the array.
CREATE INDEX tracks_artist_mbid_idx ON tracks USING gin (artist_mbid);

-- ── track_paths — where the file lives (storage fact, kept out of the catalog) ─
-- Separate table so the MB "truth" (tracks) stays free of machine-local paths:
-- identity is stable, location is volatile. `relpath` is RELATIVE to a music
-- root configured elsewhere, so the whole collection can move
-- (dock → USB → NAS) without rewriting a single row here.
CREATE TABLE track_paths (
    release_track_mbid UUID PRIMARY KEY REFERENCES tracks(release_track_mbid),
    relpath            TEXT NOT NULL,
    filesize           BIGINT,
    -- Policy as constraint: mk3 is FLAC-only.
    CONSTRAINT flac_only CHECK (lower(relpath) LIKE '%.flac')
);
