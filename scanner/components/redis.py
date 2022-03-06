
import redis
from cblock.settings import config


class RedisClient:
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=config.redis_host,
            port=config.redis_port,
            db=1,
        )

    def set_connection(self) -> None:
        self._conn = redis.Redis(connection_pool=self.pool)

    @property
    def connection(self):
        if not hasattr(self, "_conn"):
            self.set_connection()
        return self._conn
