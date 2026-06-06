from taskiq_redis import RedisStreamBroker
from context import REDIS_URI, REDIS_QUEUE

broker = RedisStreamBroker(REDIS_URI,queue_name=REDIS_QUEUE)