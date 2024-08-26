#!/usr/bin/python3

import mk3lib.musicbrainz
import mk3lib.mk3catalog

mbrainz = mk3lib.musicbrainz.Musicbrainz()
mbrainz.handshake()

catalog = mk3lib.mk3catalog.Mk3Catalog()

wanted_artists = catalog.grab_data('wanted_artists')

for i in wanted_artists:
   my_list = mbrainz.get_rgid_from_artist(i[0])
   for rgid in my_list:
       mydata = mbrainz.get_album_by_rgid(rgid)
       catalog.add_wanted_release(rgid)

my_series = catalog.grab_data("wanted_series")
for i in my_series:
    my_list = mbrainz.get_rgid_from_series(i[0])
    for rgid in my_list:
        catalog.add_wanted_release(rgid)
