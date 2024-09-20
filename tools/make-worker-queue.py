#!/usr/bin/python3

import config
import mk3lib.worker_queue

not mk3lib.worker_queue

myworkerqueue = mk3lib.worker_queue.WorkerQueue(config.queue, config.mk3_source, "\\.flac$")

myworkerqueue.create_queue()

