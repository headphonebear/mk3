# mk3 — a music-collection catalog

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-work%20in%20progress-orange.svg)

A small toolkit that turns a shelf of CDs into a database you can actually ask
questions of. **Not a player — a catalog.** It reads the tags off ripped FLAC
files and builds a PostgreSQL catalog of the collection.

## The idea

A CD is a wonderful, dumb data store. Great sound, zero metadata — no index,
no "what else is on this label", no "every studio album by this artist". Just
audio. mk3 is the index the disc never came with.

The whole thing rests on one rule: **MusicBrainz is the source of truth.** Every
album is keyed by its MusicBrainz *Release Group* ID, every track by its
*Release-Track* ID. Nothing is invented. Because the keys are real MusicBrainz
IDs, the collection's own house rules become database constraints:

- FLAC only,
- must be tagged against MusicBrainz,
- must have a Release Group — twice I've created one on MusicBrainz just so an
  album could qualify,
- and only things that actually sit on the shelf.

If a file breaks a rule, it simply can't enter the catalog. The discipline of
the collection *is* the schema.

## How it works

Three tables carry the core — the CDs on the wall, as data:

- **`albums`** — one row per Release Group (title, album artist, year, label,
  barcode, …).
- **`tracks`** — one row per physical track, linked to its album; keeps the
  MusicBrainz recording ID and the AcoustID fingerprint for later.
- **`track_paths`** — where each file lives, stored *relative* to a configurable
  music root, so the collection can move (dock → USB → NAS) without rewriting a
  single row.

Filling them is one boring, reliable pass: the **runner** walks the collection,
reads each FLAC's tags (mutagen), and upserts album/track/path (psycopg2). No
queue, no network — a local tag scan is neither slow nor rate-limited. It ships
as a small container, so it can later graduate to a proper service.

The stack:

- **PostgreSQL** — the catalog itself (the facts).
- **Valkey** (Redis-compatible) — reserved for the *slow* jobs still to come
  (MusicBrainz enrichment, FLAC→MP3), not the catalog fill.
- Both run on **chick**, the dev server in my
  [homehill](https://github.com/headphonebear/homehill) homelab.

## Running the indexer

The runner ships as a small image and runs as a **one-shot**: it starts, makes
one pass over the collection, and exits — nothing stays resident. Postgres keeps
the facts; the container is gone when it's done.

```bash
# build (on chick, from the repo copy)
docker build -t mk3-runner .

# run: music mounted read-only, the local (gitignored) config.py mounted in,
# host networking so the runner reaches the Postgres container on 127.0.0.1:5432
docker run --rm \
  -v /mnt/music:/mnt/music:ro \
  -v ~/mk3/config.py:/app/config.py:ro \
  --network host \
  mk3-runner            # add --limit 200 for a smoke test on a subset
```

The entrypoint is `tools/index.py`; everything after the image name is passed to
it:

- `--limit N` — stop after N files (smoke test),
- `--root /some/path` — index a different music root (default: `config.mk3_source`).

`config.py` is **never** baked into the image — it carries the DB password and is
mounted at runtime (see `config.py.example`). A clean run reports `ok / albums /
skipped / errored`; files missing a Release Group or Release-Track ID are skipped
by policy, not errored.

> **Note:** on chick the repo currently lives as a hand-copied folder. The intended
> path is a plain `git clone` (the repo is public) once chick has `git` — then a
> pull replaces the copy step above.

## Status & roadmap

**Works today:** the catalog. A full run indexes the whole collection cleanly —
because the tags are disciplined, it lands with zero errors.

**Next, roughly in order:**

- **Shopping lists** — set arithmetic over MusicBrainz: "every studio album by
  X" minus "what I own", plus reference lists (Rolling Stone's 500,
  *1001 Albums You Must Hear Before You Die*).
- **Enrichment** — a proper artists table, and genre/geography pulled from
  MusicBrainz / Wikipedia / Discogs, stored *as claims with provenance* rather
  than one forced truth.
- **Search & similarity** — vector search (Qdrant) for "sounds like" and
  playlist suggestions.
- **Visualization** — the collection as something you can look at, in a browser.

It's a hobby project, built on slow evenings, one thing at a time. Expect rough
edges — and expect it to get a little better with every commit.

## A peek at the data

Because a catalog only earns its keep once it can answer questions. A snapshot —
the top of the shelf by album count:

| Artist | Albums |
|---|---|
| David Bowie | 28 |
| Genesis | 21 |
| Peter Gabriel | 15 |
| Pink Floyd | 14 |
| The Beatles | 13 |

…and the whole collection skews warmly toward the 70s–90s, peaking in the 1990s.

## Credits

By **headphonebear** — the design, the ideas, and all the bugs are mine. Built
with **Claude**. And thanks to **Ana** for the refactoring and design review
that helped move the early code to OOP.

## License

MIT — use and adapt it for your own collection.
