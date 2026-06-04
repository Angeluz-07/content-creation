from taskiq_redis import RedisStreamBroker
from context import REDIS_URI

broker = RedisStreamBroker(REDIS_URI)