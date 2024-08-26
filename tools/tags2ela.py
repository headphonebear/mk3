#!/usr/bin/python3

import config
import mk3lib.scatterbrain
import mk3lib.worker_queue
import mk3lib.flactag

ela = mk3lib.scatterbrain.scatterbrain()
update = True
my_worker_queue = mk3lib.worker_queue.WorkerQueue(config.queue, config.mk3_source, "\.flac$")

while (True):
    my_result = my_worker_queue.get_next()
    if my_result != 'Done':
        my_flac = mk3lib.flactag.flactag(config.mk3_source, my_result[0], my_result[1])
        flac_json_string = my_flac.readfull()
        print(flac_json_string)
        flac_song_id = my_flac.read_songid()
        print(flac_song_id)
        ela.drop_flac(song_id=flac_song_id, tag_json_string=flac_json_string)

    else:
        break
