import json
import os

import redis

from newsCrawlerService.src.config.params import params

class RedisUtils:

    redis_pool = None

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisUtils, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.initRedis()

    def initRedis(self):
        global redis_pool
        print("PID %d: initializing redis pool..." % os.getpid())
        redis_pool = redis.ConnectionPool(host=params["redis"]["host"]
                                          , port=str(params["redis"]["port"]), decode_responses=True)


    def getConnection(self):
        return redis.Redis(connection_pool=redis_pool)


if __name__ == "__main__":
    ru = RedisUtils()
    r = ru.getConnection()
    r.hset("123", "key_a", '{"brand": "Ford", "model": "Mustang", "year": "1964"}')
    b = r.hget("123", "key_a")
    print(b)

    import time
    time.sleep(2)
    r.hset("123", "key_a", '{"brand": "Open", "model": "Astra", "year": "2004"}')
    print((r.hget("123", "key_a")))


    time.sleep(2)
    r.hset("123", "key_b", '{"brand": "HM", "model": "Ambassador", "year": "1974"}')
    print((r.hget("123", "key_b")))

    print((r.hgetall("123")))

    r.close()