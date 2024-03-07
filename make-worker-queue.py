#!/usr/bin/python3

import redis
import config
import mk3lib

redis = redis.Redis()

myworkerqueue = mk3lib.WorkerQueue(config.queue,config.mk3_source,redis,"\.jpg$|\.flac$")

redis.delete(myworkerqueue.name)
myworkerqueue.create_queue()
