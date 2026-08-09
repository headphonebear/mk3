#!/usr/bin/python3
"""mk3 catalog runner — walk the collection and fill albums / tracks / track_paths.

One pass, no queue, no network: pure mutagen (read FLAC tags) + psycopg2 (upsert).
The queue/cache machinery is for the *slow* jobs (MusicBrainz enrichment, MP3
compile); a local tag scan is neither slow nor rate-limited, so it just walks.

Run from the repo root (so `config` and `mk3lib` import):
    python3 tools/index.py                 # full collection
    python3 tools/index.py --limit 200     # smoke-test on a subset
    python3 tools/index.py --root /some/other/root
"""
import argparse
import os
import re
import sys

# make `config` and `mk3lib` importable no matter the cwd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mutagen.flac import FLAC  # noqa: E402
import config  # noqa: E402
from mk3lib.catalog import Catalog  # noqa: E402

# Track-level artist IDs (MUSICBRAINZ_ARTISTID) are now stored fully as a uuid[]
# array — feat. collaborations are kept and searchable. The one identity field we
# still store single-valued is the ALBUM artist; watch it so the full run tells us
# whether any album has >1 album-artist (a collab album) worth the same treatment.
MULTIVALUE_WATCH = (
    "MUSICBRAINZ_ALBUMARTISTID",
)


def val(audio, *keys):
    """First value across the given tag keys (fallbacks), or None."""
    for k in keys:
        v = audio.get(k)
        if v:
            return v[0]
    return None


def ival(audio, *keys):
    """Leading integer of the first present tag value, or None (handles '4/9')."""
    v = val(audio, *keys)
    if v is None:
        return None
    m = re.match(r"\s*(\d+)", str(v))
    return int(m.group(1)) if m else None


def iter_flacs(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            if name.lower().endswith(".flac"):
                yield os.path.join(dirpath, name)


def main():
    ap = argparse.ArgumentParser(description="Index the mk3 collection into Postgres.")
    ap.add_argument("--root", default=config.mk3_source, help="music root (default: config.mk3_source)")
    ap.add_argument("--limit", type=int, default=None, help="stop after N files (smoke test)")
    args = ap.parse_args()

    root = args.root
    if not os.path.isdir(root):
        sys.exit(f"music root does not exist: {root}")

    cat = Catalog()
    seen_albums = set()
    ok = skipped = errored = 0
    multi = []          # (relpath, field, n_values)
    skips = []          # (relpath, reason)  — policy skips
    errors = []         # (relpath, message) — read/DB errors

    print(f"indexing {root}")
    for n, path in enumerate(iter_flacs(root), start=1):
        if args.limit and n > args.limit:
            n -= 1
            break
        relpath = os.path.relpath(path, root)

        try:
            audio = FLAC(path)
        except Exception as e:
            errored += 1
            errors.append((relpath, f"read: {e}"))
            continue

        rgid = val(audio, "MUSICBRAINZ_RELEASEGROUPID")
        rtid = val(audio, "MUSICBRAINZ_RELEASETRACKID")
        if not rgid or not rtid:
            skipped += 1
            skips.append((relpath, "no RGID / RELEASETRACKID"))
            continue

        for f in MULTIVALUE_WATCH:
            vals = audio.get(f) or []
            if len(vals) > 1:
                multi.append((relpath, f, len(vals)))

        album = {
            "rgid": rgid,
            "release_mbid": val(audio, "MUSICBRAINZ_ALBUMID"),
            "title": val(audio, "ALBUM"),
            "album_artist": val(audio, "ALBUMARTIST"),
            "album_artist_sort": val(audio, "ALBUMARTISTSORT"),
            "album_artist_mbid": val(audio, "MUSICBRAINZ_ALBUMARTISTID"),
            "original_date": val(audio, "ORIGINALDATE"),
            "original_year": ival(audio, "ORIGINALYEAR"),
            "primary_type": val(audio, "RELEASETYPE"),
            "label": val(audio, "LABEL"),
            "catalog_number": val(audio, "CATALOGNUMBER"),
            "barcode": val(audio, "BARCODE"),
            "release_country": val(audio, "RELEASECOUNTRY"),
            "media": val(audio, "MEDIA"),
            "total_discs": ival(audio, "DISCTOTAL", "TOTALDISCS"),
            "total_tracks": ival(audio, "TRACKTOTAL", "TOTALTRACKS"),
        }
        track = {
            "release_track_mbid": rtid,
            "rgid": rgid,
            "recording_mbid": val(audio, "MUSICBRAINZ_TRACKID"),
            "title": val(audio, "TITLE"),
            "artist": val(audio, "ARTIST"),
            "artist_sort": val(audio, "ARTISTSORT"),
            # ALL track-artist IDs (feat. tracks carry several) → uuid[] array, or None
            "artist_mbid": list(audio.get("MUSICBRAINZ_ARTISTID") or []) or None,
            "disc_number": ival(audio, "DISCNUMBER"),
            "track_number": ival(audio, "TRACKNUMBER"),
            "isrc": val(audio, "ISRC"),
            "acoustid": val(audio, "ACOUSTID_ID"),
        }

        cat.savepoint()
        try:
            if rgid not in seen_albums:
                cat.upsert_album(album)          # FK target — must exist before the track
            cat.upsert_track(track)
            cat.upsert_path(rtid, relpath, os.path.getsize(path))
            cat.release()
            seen_albums.add(rgid)
            ok += 1
        except Exception as e:
            cat.rollback_file()
            errored += 1
            errors.append((relpath, f"db: {e}"))

        if n % 1000 == 0:
            cat.commit()
            print(f"  [{n}] {relpath}")

    cat.commit()
    cat.close()

    print("\n── done ──")
    print(f"  ok:       {ok}")
    print(f"  albums:   {len(seen_albums)}")
    print(f"  skipped:  {skipped}  (missing RGID / RELEASETRACKID — policy)")
    print(f"  errored:  {errored}")

    if multi:
        print(f"\n── multi-value identity fields: {len(multi)} occurrence(s) — REVIEW before deciding array vs artists table ──")
        for relpath, f, k in multi[:50]:
            print(f"  {f}  ×{k}   {relpath}")
        if len(multi) > 50:
            print(f"  … and {len(multi) - 50} more")

    if skips:
        print(f"\n── skipped (policy): {len(skips)} ──")
        for relpath, reason in skips[:30]:
            print(f"  {relpath}: {reason}")
        if len(skips) > 30:
            print(f"  … and {len(skips) - 30} more")

    if errors:
        print(f"\n── errors: {len(errors)} ──")
        for relpath, msg in errors[:30]:
            print(f"  {relpath}: {msg}")
        if len(errors) > 30:
            print(f"  … and {len(errors) - 30} more")


if __name__ == "__main__":
    main()
