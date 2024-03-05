import json
import os
import re
import redis
import config

class WorkerQueue:
    mk3_source = ''
    name = ''
    # regex = '\.jpg$'
    # regex = '\.flac$'
    regex = '\.jpg$|\.flac$'
    def create_queue(self):
        print(self.regex)
        mk3_tree = os.walk(self.mk3_source)
        for path, directories, files in mk3_tree:
            directories.sort()
            files = sorted(files)
            for file in files:
                if re.search(self.regex,file):
                    redis.rpush(self.name, json.dumps((path, file)))
        return()

redis = redis.Redis()

myworkerqueue = WorkerQueue()
myworkerqueue.mk3_source = config.mk3_source
myworkerqueue.name = 'newqueue'
myworkerqueue.create_queue()
