#!/usr/bin/python3

import config
import mk3lib
import json
import os

update = True
myworkerqueue = mk3lib.WorkerQueue(config.queue,config.mk3_source,"\\.flac$")

while (True):
    myresult = myworkerqueue.get_next()
    if myresult != 'Done':
        myflac = mk3lib.flactag(config.mk3_source, myresult[0], myresult[1])
        flac_json_string = myflac.readfull()
        print(flac_json_string)
        #print(myflac.read_songid())

    else:
        break

