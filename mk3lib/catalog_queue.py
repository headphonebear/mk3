import redis

class CatalogQueue:
    def __init__(self):
        self.redis = redis.Redis()

    def rgid_put(self, rgid):

        if not self.redis.sismember('release_set', rgid):
            # Add ID to the set to ensure uniqueness
            self.redis.sadd('release_set', rgid)
            # Add ID to the queue
            self.redis.rpush('release_queue', rgid)
            return True  # Indicate that the ID was added
        return False  # Indicate that the ID was already present

    def rgid_get(self):

        rgid = self.redis.lpop('release_queue')
        if rgid:
            release_group_id = rgid.decode('utf-8')
            return release_group_id
        return None