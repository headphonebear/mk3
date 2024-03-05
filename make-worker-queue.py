#!/usr/bin/python3

import redis
import config
import mk3lib

redis = redis.Redis()

myworkerqueue = mk3lib.WorkerQueue()
myworkerqueue.mk3_source = config.mk3_source
myworkerqueue.name = config.queue
myworkerqueue.redis = redis
redis.delete(myworkerqueue.name)
myworkerqueue.create_queue()
