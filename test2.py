import redis

redis = redis.Redis()

while True:
    thingy = redis.lpop('newqueue')
    if thingy == None:
        break
    print (thingy)


