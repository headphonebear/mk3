import json
import os
import redis
import config

class WorkerQueue:
    mk3_source = ''
    name = ''
    def create_queue(self):
        mk3_tree = os.walk(self.mk3_source)
        for path, directories, files in mk3_tree:
            directories.sort()
            files = sorted(files)
            for file in files:
                redis.rpush(self.name, json.dumps((path, file)))
        return()

redis = redis.Redis()

myworkerqueue = WorkerQueue()
myworkerqueue.mk3_source = config.mk3_source
myworkerqueue.name = 'newqueue'
myworkerqueue.create_queue()
