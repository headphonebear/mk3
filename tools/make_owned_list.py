#!/usr/bin/python3

import config
import mk3lib.worker_queue
import mk3lib.flactag
import mk3lib.mk3catalog

catalog = mk3lib.mk3catalog.Mk3Catalog()

my_worker_queue = mk3lib.worker_queue.WorkerQueue(config.queue, config.mk3_source, "\.flac$")

while True:
    my_result = my_worker_queue.get_next()
    if my_result != 'Done':
        my_flac = mk3lib.flactag.flactag(config.mk3_source, my_result[0], my_result[1])
        rgid = my_flac.read_rgid()
        catalog.add_rgid_to_table(rgid,"owned_releases")
    else:
        break