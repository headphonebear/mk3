#!/usr/bin/python3

import config
import mk3lib

ela = mk3lib.scatterbrain()
update = True
myworkerqueue = mk3lib.WorkerQueue(config.queue, config.mk3_source, "\.flac$")

while (True):
    myresult = myworkerqueue.get_next()
    if myresult != 'Done':
        myflac = mk3lib.flactag(config.mk3_source, myresult[0], myresult[1])
        flac_json_string = myflac.readfull()
        print(flac_json_string)
        flac_song_id = myflac.read_songid()
        print(flac_song_id)
        ela.drop_flac(song_id=flac_song_id, tag_json_string=flac_json_string)

    else:
        break
