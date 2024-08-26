#!/usr/bin/python3

import config
import mk3lib.worker_queue
import mk3lib.flactag

my_worker_queue = mk3lib.worker_queue.WorkerQueue(config.queue, config.mk3_source, "\\.flac$")
my_artist_list = set()

x = 0

while (True):
    my_result = my_worker_queue.get_next()
    if my_result != 'Done':
        my_flac = mk3lib.flactag.flactag(config.mk3_source, my_result[0], my_result[1])
        # print(myflac.readfull())
        album_artist_id = my_flac.read_albumartistids()
        album_artist = my_flac.read_albumartist()
        print(album_artist_id, album_artist)
        for artist_id in album_artist_id:
            my_artist_list.add((artist_id, album_artist))
    else:
        break

for i in my_artist_list:
    print(i[0],"+++", i[1])