#!/usr/bin/python3

import config
import mk3lib

myworkerqueue = mk3lib.WorkerQueue(config.queue,config.mk3_source,"\.flac$")

myworkerqueue.create_queue()
