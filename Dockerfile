# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  mk3 catalog runner — one-shot indexer (walk FLACs → Postgres)             ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
# A proper image so this can graduate to a belfry microservice later. glibc
# base (slim) keeps psycopg2-binary a clean wheel install — no musl source build.
#
# Build (on chick, from the repo copy):   docker build -t mk3-runner .
# Run (mount music read-only + the local, secret config.py; host net reaches
# the postgres container on 127.0.0.1:5432):
#   docker run --rm \
#     -v /mnt/music:/mnt/music:ro \
#     -v ~/mk3/config.py:/app/config.py:ro \
#     --network host \
#     mk3-runner --limit 200
FROM python:3.12-slim

# ONLY what the runner needs — deliberately NOT the legacy kitchen-sink
# requirements.txt (no elasticsearch / redis / ffmpeg here).
RUN pip install --no-cache-dir mutagen psycopg2-binary

WORKDIR /app
COPY mk3lib/ ./mk3lib/
COPY tools/ ./tools/
# config.py is NOT baked in — it carries the DB password and is mounted at runtime.

ENTRYPOINT ["python", "tools/index.py"]
