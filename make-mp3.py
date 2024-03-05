#!/usr/bin/python3

import redis
import config
import mk3lib

redis = redis.Redis()

myworkerqueue = mk3lib.WorkerQueue()
myworkerqueue.mk3_source = config.mk3_source
myworkerqueue.name = config.queue
myworkerqueue.redis = redis

mynewmp3 = mk3lib.Mp3Compiler()
mynewmp3.mk3_source = config.mk3_source
mynewmp3.out_path = config.mp3_out

myresult = True

while myresult != None:
    myresult=myworkerqueue.get_next()
    mynewmp3.in_path = myresult[0]
    mynewmp3.in_file = myresult[1]
    mynewmp3.make()