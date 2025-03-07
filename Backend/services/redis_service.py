import redis

class RedisService:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        return cls._client
