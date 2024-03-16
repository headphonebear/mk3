#!/usr/bin/python3

import config
import mk3lib
import os

up_counter = 0
new_counter = 0
update = True
myworkerqueue = mk3lib.WorkerQueue(config.queue,config.mk3_source,"\.flac$")

while (True):
    myresult = myworkerqueue.get_next()
    if myresult != 'Done':
        mynewmp3 = mk3lib.Mp3Compiler(config.mk3_source, config.mp3_out, myresult[0], myresult[1], False,"320k")
        if not os.path.exists(mynewmp3.mp3_new_path + mynewmp3.in_path):
            os.makedirs(mynewmp3.mp3_new_path + mynewmp3.in_path)
        if not os.path.isfile(mynewmp3.mp3_fullpath):
            mynewmp3.compile()
            mynewmp3.copy_tags()
            mynewmp3.add_picture()
            new_counter = new_counter + 1
        else:
            if update == True:
                mynewmp3.copy_tags()
                mynewmp3.add_picture()
            up_counter = up_counter + 1
    else:
        break

print("Done")
print("New", new_counter)
print("Updated", up_counter)
