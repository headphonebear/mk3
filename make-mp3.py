#!/usr/bin/python3

import config
import mk3lib.worker_queue
import mk3lib.mk3_compiler
import os

up_counter = 0
new_counter = 0
update = True
my_worker_queue = mk3lib.worker_queue.WorkerQueue(config.queue, config.mk3_source, "\.flac$")

while True:
    my_result = my_worker_queue.get_next()
    if my_result != 'Done':
        my_new_mp3 = mk3lib.mk3_compiler.Mp3Compiler(config.mk3_source, config.mp3_out, my_result[0], my_result[1], False, "320k")
        if not os.path.exists(my_new_mp3.mp3_new_path + my_new_mp3.in_path):
            os.makedirs(my_new_mp3.mp3_new_path + my_new_mp3.in_path)
        if not os.path.isfile(my_new_mp3.mp3_fullpath):
            my_new_mp3.compile()
            my_new_mp3.copy_tags()
            my_new_mp3.add_picture()
            new_counter = new_counter + 1
        else:
            if update:
                my_new_mp3.copy_tags()
                my_new_mp3.add_picture()
            up_counter = up_counter + 1
    else:
        break

print("Done")
print("New", new_counter)
print("Updated", up_counter)
