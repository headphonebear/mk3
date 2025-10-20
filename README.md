# 🎵 mk3 - Music Collection Toolkit

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-work%20in%20progress-orange.svg)

> **A powerful Python toolkit for managing, processing, and enriching your music collection**

mk3 is a comprehensive music collection management system that handles FLAC-to-MP3 conversion, metadata enrichment via MusicBrainz, and provides powerful search capabilities through Elasticsearch integration.

## 🚀 What it does

- **🎧 Audio Processing**: Convert FLAC files to MP3 with tag preservation and cover art
- **🔍 Metadata Enrichment**: Automatic MusicBrainz integration for comprehensive album/artist data
- **⚡ Queue Processing**: Redis-based worker queues for efficient batch operations
- **🗄️ Data Management**: PostgreSQL storage for collection catalogs and metadata
- **🔎 Search & Discovery**: Elasticsearch integration for advanced music discovery
- **🐳 Containerized**: Docker support for easy deployment and scaling

## 📋 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FLAC Files    │───▶│   mk3 Library   │───▶│   MP3 Output    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │◀───│  Redis Queue   │───▶│ Elasticsearch   │
│   (Metadata)    │    │   (Processing) │    │   (Search)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               ▲
                               │
                    ┌─────────────────┐
                    │  MusicBrainz    │
                    │    (API)        │
                    └─────────────────┘
```

## 🛠️ Core Modules

### `mk3lib/`
- **`flactag.py`** - FLAC metadata extraction with Redis caching
- **`musicbrainz.py`** - MusicBrainz API integration with smart caching
- **`mk3_compiler.py`** - Audio conversion and processing pipeline
- **`mk3catalog.py`** - PostgreSQL database operations
- **`scatterbrain.py`** - Elasticsearch indexing and search
- **`worker_queue.py`** - Redis queue management
- **`catalog_queue.py`** - Collection cataloging workflows

### `tools/`
- **`make-mp3.py`** - Convert FLAC to MP3 with metadata
- **`make-worker-queue.py`** - Generate processing queues
- **`make_owned_list.py`** - Generate collection inventories
- **`make_shoppinglist.py`** - Track missing albums
- **`tags2ela.py`** - Index metadata to Elasticsearch

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis server
- PostgreSQL database
- Elasticsearch (optional, for search features)
- FFmpeg (for audio conversion)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/headphonebear/mk3.git
cd mk3
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure your setup**
```bash
cp config.dev.py config.py
# Edit config.py with your paths and database settings
```

4. **Set up the database**
```bash
psql -U postgres -d mk3 -f tables.sql
```

### Docker Setup

```bash
# Build and run with Docker
docker-compose up -d

# Or build manually
docker build -t mk3 .
docker run -v /path/to/music:/music mk3
```

## 📖 Usage Examples

### Basic FLAC to MP3 Conversion
```python
from mk3lib.flactag import flactag
from mk3lib.mk3_compiler import Mk3Compiler

# Read FLAC tags
flac = flactag(in_path="/album/", in_file="track.flac")
tags = flac.readfull()

# Convert to MP3
compiler = Mk3Compiler()
compiler.compile_mp3("/path/to/flac", "/path/to/mp3")
```

### MusicBrainz Integration
```python
from mk3lib.musicbrainz import Musicbrainz

mb = Musicbrainz()
mb.handshake()

# Get album info by release group ID
album_info = mb.get_album_by_rgid("your-rgid-here")
print(f"Album: {album_info['title']} by {album_info['artist']} ({album_info['year']})")
```

### Queue Processing
```python
from mk3lib.worker_queue import WorkerQueue

# Create processing queue
queue = WorkerQueue()
queue.add_files_to_queue("/path/to/flac/collection")

# Process queue items
while not queue.is_empty():
    item = queue.get_next()
    # Process your files here
```

## 🔧 Configuration

Edit `config.py` to match your setup:

```python
# Music collection paths
mk3_source = '/path/to/flac/collection/'
mp3_out = '/path/to/mp3/output/'

# Database settings
psql_host = "localhost"
psql_dbname = "mk3"
psql_user = "your_user"
psql_password = "your_password"

# MusicBrainz API
musicbrainzngs_app = 'your_app_name'
musicbrainzngs_contact = 'your@email.com'
```

## 📚 Database Schema

The system uses PostgreSQL tables defined in `tables.sql`:

- Collection catalogs and metadata storage
- Artist and album relationships
- Processing queue states
- Search index mappings

## 🔍 Features in Detail

### Smart Caching
- Redis-based caching for MusicBrainz API calls
- FLAC metadata caching to speed up repeated operations
- Configurable cache expiration

### Batch Processing
- Queue-based processing for large collections
- Resumable operations
- Progress tracking and error handling

### Metadata Enrichment
- Automatic MusicBrainz lookups
- Tag standardization and cleanup
- Cover art preservation and embedding

## 🚧 Development Status

This project is actively developed as a hobby project. Current focus areas:

- [ ] Improved error handling and logging
- [ ] Web interface for collection management
- [ ] Enhanced Docker orchestration
- [ ] API development for external integrations
- [ ] Advanced search and filtering capabilities

## 🤝 Contributing

This is a personal hobby project, but suggestions and improvements are welcome! 

## 📝 License

MIT License - Feel free to use and modify for your own music collection needs.

## 🎵 Philosophy

> "Finally getting better at things I started long ago, instead of starting something new."

This project represents a commitment to refining and perfecting existing ideas rather than constantly chasing new ones. It's about building something solid, useful, and maintainable for long-term music collection management.

---

**Note**: This software is work in progress. Expect rough edges, but also expect a system that gets better with every commit! 🚀