import redis

redis = redis.Redis()

while True:
    thingy = redis.lpop('workerqueue')
    if thingy == None:
        break
    print (thingy)


