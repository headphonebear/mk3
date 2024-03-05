import redis

redis = redis.Redis()

print (redis.lpop('newqueue'))
print (redis.lpop('newqueue'))
print (redis.lpop('newqueue'))