import json
import os
import re
import redis

class WorkerQueue:
    def __init__(self, name:str="", mk3_source:str="", regex:str="\\.jpg$|\\.flac$"):
        self.name = name
        self.mk3_source = mk3_source
        self.redis = redis.Redis()
        self.regex = regex
        self.path = ''
        self.file = ''

    def create_queue(self):
        mk3_tree = os.walk(self.mk3_source)
        for path, directories, files in mk3_tree:
            directories.sort()
            files = sorted(files)
            for file in files:
                if re.search(self.regex, file):
                    self.redis.rpush(self.name, json.dumps((path[len(self.mk3_source):]+"/", file)))
        return True

    def get_next(self):
        from_redis = self.redis.lpop(self.name)
        if (from_redis != None):
            self.path = json.loads(from_redis)[0]
            self.file = json.loads(from_redis)[1]
            return self.path, self.file
        else:
            return 'Done'