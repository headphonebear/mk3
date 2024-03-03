import json
import os
import redis
import config

class Filelist:
    mk3_source = ''
    def create_filelist(self):
        mk3_tree = os.walk(self.mk3_source)
        filelist = []
        for path, directories, files in mk3_tree:
            directories.sort()
            files = sorted(files)
            for file in files:
                element = path, file
                filelist.append(element)
        return(filelist)

class Workerqueue:
    filelist = ''
    name = ''
    def create_queue(self):
        for line in range(len(self.filelist)):
            print(self.filelist[line])
            jsondata = json.dumps(self.filelist[line])
            redis.rpush(self.name,jsondata)
        return()


redis = redis.Redis()

myfilelist = Filelist()
myfilelist.mk3_source = config.mk3_source
testfilelist = myfilelist.create_filelist()

myWorkerqueue = Workerqueue()
myWorkerqueue.filelist = testfilelist
myWorkerqueue.name = 'firstqueue'
myWorkerqueue.create_queue()

print (redis.lpop(myWorkerqueue.name))
print (redis.lpop(myWorkerqueue.name))
print (redis.lpop(myWorkerqueue.name))