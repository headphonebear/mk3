
import config
import mk3lib

myworkerqueue = mk3lib.WorkerQueue(config.queue)

while True:
    result = myworkerqueue.get_next()
    if result == 'Done':
        break
    print(result)




