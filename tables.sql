CREATE TABLE wanted_releases (
    rgid UUID PRIMARY KEY,
    title TEXT NOT NULL,
    artist_id UUID NOT NULL,
    artist_name TEXT NOT NULL,
    year SMALLINT NOT NULL
);

CREATE TABLE wanted_artists (
    artist_id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE wanted_series (
    series_id UUID PRIMARY KEY,
    name TEXT NOT NULL
);
