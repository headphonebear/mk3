CREATE TABLE wanted_releases (
    rgid UUID PRIMARY KEY
);

CREATE TABLE wanted_artists (
    artist_id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE wanted_series (
    series_id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE owned_releases (
    rgid UUID PRIMARY KEY
);

