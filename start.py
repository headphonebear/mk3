import redis
import config

import mk3lib

redis = redis.Redis()

myworkerqueue = mk3lib.WorkerQueue()
myworkerqueue.mk3_source = config.mk3_source
myworkerqueue.name = 'newqueue'
myworkerqueue.redis = redis
#redis.delete(myworkerqueue.name)
#myworkerqueue.create_queue()

myresult=myworkerqueue.get_next()
print(myresult[0])
print(myresult[1])

mynewmp3 = mk3lib.Mp3Compiler()
mynewmp3.mk3_source = config.mk3_source
mynewmp3.out_path = config.mp3_out
mynewmp3.in_path = myresult[0]
mynewmp3.in_file = myresult[1]
mynewmp3.make()