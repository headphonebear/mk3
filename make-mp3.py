#!/usr/bin/python3

import config
import mk3lib
import os

myworkerqueue = mk3lib.WorkerQueue(config.queue,config.mk3_source,"\.flac$")

while (True):
    myresult = myworkerqueue.get_next()
    if myresult != 'Done':
        mynewmp3 = mk3lib.Mp3Compiler(config.mk3_source, config.mp3_out, myresult[0], myresult[1], False,"320k")
        if not os.path.exists(mynewmp3.out_mp3):
            os.makedirs(mynewmp3.out_mp3)
        if not os.path.isfile(mynewmp3.out_mp3_full):
            mynewmp3.compile()
            mynewmp3.copy_tags()
            mynewmp3.add_picture()
    else:
        break

print("Done")
