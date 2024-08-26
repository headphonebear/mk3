import config
import mk3lib

myworkerqueue = mk3lib.WorkerQueue(config.queue)

print (myworkerqueue.get_next())
print (myworkerqueue.get_next())
print (myworkerqueue.get_next())
