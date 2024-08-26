#!/usr/bin/python3

import mk3lib.musicbrainz
import mk3lib.mk3catalog

# says hi to Musicbrainz and database

mbrainz = mk3lib.musicbrainz.Musicbrainz()
mbrainz.handshake()

catalog = mk3lib.mk3catalog.Mk3Catalog()

# writes all rgid from all wanted artists into database

wanted_artists = catalog.grab_data('wanted_artists')

for i in wanted_artists:
    my_list = mbrainz.get_rgid_from_artist(i[0])
    for rgid in my_list:
        mydata = mbrainz.get_album_by_rgid(rgid)
        catalog.add_rgid_to_table(rgid,"wanted_releases")

# adds all rgid from wanted series

my_series = catalog.grab_data("wanted_series")
for i in my_series:
    my_list = mbrainz.get_rgid_from_series(i[0])
    for rgid in my_list:
        catalog.add_rgid_to_table(rgid,"wanted_releases")